function calculateAspectRatioFit(srcWidth, srcHeight, maxWidth, maxHeight) {
  var ratio = Math.min(maxWidth / srcWidth, maxHeight / srcHeight);

  return { width: srcWidth*ratio, height: srcHeight*ratio };
}

(function ($) {
  $("document").ready(function () {
    $("img.thumbnail").each(function () {
      srcWidth = $(this).width()
      srcHeight = $(this).height()
      maxWidth = parseInt($(this).data("width"))
      maxHeight = parseInt($(this).data("height"))
      resized = calculateAspectRatioFit(srcWidth, srcHeight, maxWidth, maxHeight)
      $(this).width(resized.width)
      $(this).height(resized.height)
    })
  })
})(jQuery || django.jQuery)
