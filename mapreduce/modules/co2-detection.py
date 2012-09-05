import numpy

import GeoPictureSerializer

def newBand(geoPicture, discard=["B183", "B184", "B185", "B186", "B188", "B189"]):
    # prepare the output; the main function gets to decide if it wants to see the input again
    outputBands = []
    for band in geoPicture.bands:
        if band not in discard:
            outputBands.append(band)
    
    output = numpy.empty((geoPicture.picture.shape[0], geoPicture.picture.shape[1], len(outputBands) + 1), dtype=numpy.float)
    for band in outputBands:
        output[:,:,outputBands.index(band)] = geoPicture.picture[:,:,geoPicture.bands.index(band)]

    outputBands.append("CO2")

    # if you don't have all of the bands needed to evaluate this analytic, give up
    if "B183" not in geoPicture.bands or \
       "B184" not in geoPicture.bands or \
       "B185" not in geoPicture.bands or \
       "B186" not in geoPicture.bands or \
       "B188" not in geoPicture.bands or \
       "B189" not in geoPicture.bands:
        output[:,:,outputBands.index("CO2")] = 0.

        geoPictureOutput = GeoPictureSerializer.GeoPicture()
        geoPictureOutput.metadata = geoPicture.metadata
        geoPictureOutput.bands = outputBands
        geoPictureOutput.picture = output
        return geoPictureOutput

    # Work in the log-radiance space (and offset zeros by a tenth of a resolution unit)
    B183 = numpy.log(geoPicture.picture[:,:,geoPicture.bands.index("B183")] + 0.1/80.)
    B184 = numpy.log(geoPicture.picture[:,:,geoPicture.bands.index("B184")] + 0.1/80.)
    B185 = numpy.log(geoPicture.picture[:,:,geoPicture.bands.index("B185")] + 0.1/80.)
    B186 = numpy.log(geoPicture.picture[:,:,geoPicture.bands.index("B186")] + 0.1/80.)
    B188 = numpy.log(geoPicture.picture[:,:,geoPicture.bands.index("B188")] + 0.1/80.)
    B189 = numpy.log(geoPicture.picture[:,:,geoPicture.bands.index("B189")] + 0.1/80.)

    # the first three are just numbers
    sum1 = 4.
    sumx = 183. + 184. + 188. + 189.
    sumxx = 183.**2 + 184.**2 + 188.**2 + 189.**2
    # the last two are images (2-D arrays)
    sumy = B183 + B184 + B188 + B189
    sumxy = 183.*B183 + 184.*B184 + 188.*B188 + 189.*B189

    delta = sum1*sumxx - sumx**2
    constant = (sumxx*sumy - sumx*sumxy) / delta
    linear = (sum1*sumxy - sumx*sumy) / delta

    # How high are the peaks above the linear background?
    firstpeak = (B185 - (constant + 185.*linear))/2. + (B186 - (constant + 186.*linear))/2.

    # Negate it (because they're absorbtion peaks) and re-exponentiate
    output[:,:,outputBands.index("CO2")] = numpy.exp(-firstpeak)

    geoPictureOutput = GeoPictureSerializer.GeoPicture()
    geoPictureOutput.metadata = geoPicture.metadata
    geoPictureOutput.bands = outputBands
    geoPictureOutput.picture = output
    return geoPictureOutput
