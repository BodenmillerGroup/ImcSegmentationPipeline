library(CATALYST)
library(data.table)
library(flowCore)
library(dplyr)
library(dtplyr)
library(stringi)
# author: Vito Zanotelli et al.

col2img <- function(dat, valcol, xcol = 'X', ycol = 'Y') {
  xmax <- dat[, max(get(xcol))]
  ymax <- dat[, max(get(ycol))]
  # sometimes the last row is incomplete, thus only take the data until the second last row in this case
  if (xmax < dat[, get(xcol)[.N]]) {
    ymax <- ymax - 1
  }
  xmax <- xmax + 1
  ymax <- ymax + 1

  img <- matrix(data = dat[1:(xmax * ymax), get(valcol)], nrow = xmax, ncol = ymax)
  return(img)
}

img2dat <- function(imgdat) {
  imgdat <- copy(imgdat)
  dat <- imgdat

  colnames(dat) <- sapply(colnames(dat), function(x) gsub('.*\\(', '', x))
  colnames(dat) <- sapply(colnames(dat), function(x) gsub('\\)', '', x))
  return(dat)
}


### Helpers to load single stain .txt files

load_ss_fol <- function(fol_ss) {
  # helper function to load all .txt files from a folder
  fns_txt <- list.files(fol_ss, pattern = '*.[0-9]+.txt$')
  imgs.ss <- lapply(fns_txt, function(x) {
    fread(file.path(fol_ss, x)) })
  names(imgs.ss) <- fns_txt
  return(imgs.ss)
}


load_ss_zip <- function(fol_ss) {
  # helper function that can load .txt files form a .zip file archive
  fns_inzip <- unzip(fol_ss, list = T) %>%
    do(as.data.frame(.$Name[endsWith(.$Name, '.txt')]))

  fns_inzip <- fns_inzip[, 1]
  imgs.ss <- lapply(fns_inzip, function(x) {
    fread(cmd = paste0('unzip -qp ', fol_ss, ' ', gsub(" ", '\\\\ ', x)))
  })

  names(imgs.ss) <- fns_inzip
  return(imgs.ss)
}


### 

get_metals_from_txtname <- function(nam) {
  nam <- gsub('.*\\(', '', nam)
  nam <- gsub('\\)', '', nam)
  return(nam)
}

fixnames <- function(imgdat) {
  # Extracts the correct metal names from the .txt files
  imgdat <- copy(imgdat)
  dat <- imgdat
  colnames(dat) <- sapply(colnames(dat), function(x) get_metals_from_txtname(x))
  return(dat)
}

imglist2dat <- function(datlist) {
  #  creates a data file from the list of files
  imgdat <- rbindlist(datlist, fill = T, idcol = 'file')
  return(imgdat)
}

## Helper to summarize

calc_file_medians <- function(dat) {
  # calculates medians per file
  tdat <- dat %>%
    dplyr::select(-c(Start_push, End_push, Pushes_duration, X, Y, Z)) %>%
    melt.data.table(id.vars = c('metal', 'mass', 'file')) %>%
    do(data.table(.)[, list(med = median(value)), by = .(variable, metal, mass, file)])
  return(tdat)

}


## Helpers to aggregate consecutive pixels

get_consecutive_bin <- function(nel, nbin) {
  # gets consecutive pixels
  idx <- rep(1:ceiling(nel / nbin), each = nbin)
  return(idx[1:nel])
}

aggregate_pixels <- function(dat, n) {
  # sums over n consecutive pixels
  tdat <- dat[, rowsum(.SD, get_consecutive_bin(.N, n)), by = .(file, mass, metal)]
  return(tdat)
}


## Do compensation

filter_rare_bc <- function(re, minevents) {
  # allows filtering out of rare events
  stats <- table(re@bc_ids)
  nonfreq <- names(stats)[stats < minevents]
  re@bc_ids[re@bc_ids %in% nonfreq] <- '0'
  return(re)

}

ensure_correct_bc <- function(re, mass) {
  # enforces correct barcodes according to mass/metal identified from the file name
  re@bc_ids[re@bc_ids != as.character(mass)] <- '0'
  return(re)
}


re_from_dat <- function(dat, ss_ms, minevents = 10, correct_bc = NULL) {
  # Debarcode the data, enforce some minimal quality
  # dat: data
  # bc_ms: list of masses used for the single stains
  # minevents: minimum number of events a metal needs to have to be considered
  # correct_bc: list of ground truth barcodes, e.g. from the filenames
  ff <- dat %>%
    dplyr::select(-c(file, mass, metal)) %>%
    as.matrix.data.frame() %>%
    flowFrame()


  re <- CATALYST::assignPrelim(x = ff, y = ss_ms)
  re <- estCutoffs(re)
  re <- applyCutoffs(re)

  # filter for conditions with less then minevents
  if (!is.null(correct_bc) && correct_bc) {
    re <- ensure_correct_bc(re, dat[, mass])
  }

  re <- filter_rare_bc(re, minevents)
  return(re)
}


sm_from_dat <- function(dat, ss_ms, minevents = 10, remove_incorrect_bc = T, ...) {
  # Helper function to debarcode and calculate spillover
  # ss_ms: masses used for single stains
  # minevents: minimal number of events to consider spillover estimation
  # remove_incorrect_bc; enforce correct barcode by using
  re <- re_from_dat(dat, ss_ms, minevents, remove_incorrect_bc)
  sm <- computeSpillmat(re, ...)
  return(sm)
}


#' Estimates spillover directly from a folder containing IMC .txt files
#'
#' @param fol_ss folder containing .txt acquisitions of IMC single stains
#' @param ssmetals_from_fn logical, Are the single stains correctly named xxx_x_metal_x.txt? (E.g. Dy161 1-1000_8_Dy161_8.txt
#' @param ssmass Vector of masses of the single stains used. Required if ssmetals_from_file_fn is False
#' @param fn2ssmetal Optional: a named vector mapping the filenames to the single stain metal used (e.g. if it cannot be parsed from the filename)
#' @param remove_incorrect_bc Remove barcodes not matching the filename single stain annotation (requires either ssmetals_from_fn=T or fn2ssmetal )
#' @param minevents Minimal number of events (after debarcoding) that need to be present in a single stain in order that a spillover estimation is performed
#' @param bin_n_pixels Optional: integer, bin n consecutive pixels. Can be used if the intensities per pixel are to low (e.g. <200 counts)
#' @param ... Optional parameters will be passed to CATALYST::computeSpillmat 
#' @return a list containing the spillover matrix (sm), the data (data) and the debarcoded Catalyst object (re)

estimate_sm_from_imc_txtfol <- function(fol_ss, ssmetals_from_fn = F, ssmass = NULL, fn2ssmetal = NULL,
                                        remove_incorrect_bc = FALSE, minevents = 10, bin_n_pixels = 1, ...) {
  imgs_ss <- load_ss_fol(fol_ss)
  imgs_ss <- lapply(imgs_ss, fixnames)
  imgdat <- imglist2dat(imgs_ss)

  if (ssmetals_from_fn) {
    imgdat[, metal := strsplit(.BY[[1]], '_')[[1]][3], by = file]
    imgdat[, mass := as.numeric(str_extract_all(.BY[[1]], "[0-9]+")[[1]]), by = metal]
  } else {
    imgdat[, ':='(metal = NaN, mass = NaN)]
  }
  if (ssmetals_from_fn) {
    ssmass <- imgdat[, unique(mass)]
  } else if (is.null(ssmass)) {
    raise('If ssmetals cannot be derived from filenames, they need to be manually
          provided using the "ssmetals" parameter!
          ')
  }

  if (bin_n_pixels > 1) {
    imgdat <- aggregate_pixels(imgdat, bin_n_pixels)
  }
  re <- re_from_dat(imgdat, ssmass, minevents, correct_bc = remove_incorrect_bc)
  sm <- computeSpillmat(re, ...)
  return(list('sm' = sm, 'data' = imgdat, 're' = re))
}

plot_file_medians <- function(dat) {
  pdat <- calc_file_medians(dat)
  p <- pdat %>%
    ggplot(aes(x = 1, y = med)) +
    facet_wrap(~file + metal, scales = 'free_y') +
    geom_label(aes(label = variable))
  return(p)
}

#' Estimates spillover directly from a folder containing IMC .txt files
#'
#' @param a imc acquisition loaded as a data.table

comp_datimg <- function(datimg, sm, method = 'nnls', ...) {
  orig_names <- colnames(img)
  metal_names <- sapply(orig_names, get_metals_from_txtname)
  img_mat <- as.matrix(datimg)
  colnames(img_mat) <- metal_names

  img_comp <- img_mat %>%
    flowCore::flowFrame() %>%
    CATALYST::compCytof(sm, method = method, ...) %>%
    flowCore::exprs() %>%
    as.data.table()
  setnames(img_comp, orig_names)
  return(img_comp)
} 