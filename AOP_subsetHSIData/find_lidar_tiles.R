## This script will sort through a directory of raster files 
## to determine what files are within a particular study AOI extent

library(raster)
library(rgdal)
library(rgeos)

# specify the dir that you wish to find rasters
dataDir <- "/Volumes/data_dr/teakettle/lidar/CHM"
# specify the output file name
outFile <- "Teakettle_CHM.tif"
# specify the clipping file name
clipFile <- "teakettle_clip"
#specify the path to the clip file
clipFilePath <- "."
# specify the working DIR

setwd("~/Documents/data/1_spectrometerData/Teakettle")


# import shapefile
clippingExtent <- readOGR(clipFilePath, clipFile)

# get list of files from the server
rasterList <- list.files(dataDir, full.names = TRUE, pattern = "\\.tif$")

# the function below checks to see if a raster falls within an clipping extent
checkExtent <- function(raster, clipShp){
  # create polygon extent assign CRS to extent 
  rasterExtPoly <- as(extent(raster), "SpatialPolygons")
  crs(rasterExtPoly) <-  crs(clippingExtent)
  
  # check to see if the polygons overlap
  # return a boolean
  return(gIntersects(clippingExtent,rasterExtPoly))
}


rastInClip <- function(rasterFile) {
  # rasterFile <- "/Volumes/data_dr/teakettle/DTM/2013_TEAK_1_326000_4103000_DTM.tif"
  # rasterFile <- rasterList[221]
  recordRaster <- NA
  aRaster <- raster(rasterFile)
  if (checkExtent(aRaster)) {
    recordRaster <- rasterFile
  }
  return(recordRaster)
}

# create a list of only rasters in the extent window
finalList <- unlist(lapply(rasterList, rastInClip))

# remove NA and get the final list of rasters to mosaic!
finalList <- finalList[!is.na(finalList)]
  
# take the list of rasters, and create a mosaic
rast.list <- list()
for(i in 1:length(finalList)) { rast.list[i] <- stack(finalList[i]) }
  
# mosaic rasters
rast.list$fun <- mean
rast.mosaic <- do.call(mosaic,rast.list)
# plot(rast.mosaic)

# write geotiff
writeRaster(rast.mosaic,
            filename=outFile,
            format="GTiff",
            overwrite = TRUE
            )
