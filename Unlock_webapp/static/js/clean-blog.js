(function($) {
  "use strict"; // Start of use strict

  // Floating label headings for the contact form
  $("body").on("input propertychange", ".floating-label-form-group", function(e) {
    $(this).toggleClass("floating-label-form-group-with-value", !!$(e.target).val());
  }).on("focus", ".floating-label-form-group", function() {
    $(this).addClass("floating-label-form-group-with-focus");
  }).on("blur", ".floating-label-form-group", function() {
    $(this).removeClass("floating-label-form-group-with-focus");
  });

})(jQuery); // End of use strict

function footer() {
  if (window.screen.height > ($(".container").height() + 119.2)) {
    $(".identity").css("position", "absolute");
    $(".identity").css("bottom", "60px");
    $(".identity").css("margin-left", "-60px");
    $("body").css("margin", "0");
  }
  else {
    $(".identity").css("position", "relative");
    $(".identity").css("bottom", "0");
    $(".identity").css("margin-left", "0");
    $("body").css("margin", "0 0 54.2px 0");
  }
}

footer();
$(window).resize(footer);