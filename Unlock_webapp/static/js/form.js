jQuery.validator.setDefaults({
	errorPlacement: function(error, element) {
		jQuery(element).closest('div.form-group').find('.form-text').html(error.html());
	},
	highlight: function(element) {
		jQuery(element).closest('div.form-group').removeClass('has-success').addClass('has-error');
	},
	unhighlight: function(element, errorClass, validClass) {
		jQuery(element).closest('div.form-group').removeClass('has-error').addClass('has-success');
		jQuery(element).closest('div.form-group').find('.form-text').html('');
	}
});

jQuery.validator.addMethod("phone", function (phone_number, element) {
    phone_number = phone_number.replace(/\s+/g, "");
    return this.optional(element) || phone_number.length > 9 &&
          phone_number.match(/^(([+]|00)39)?((3[0-9][0-9]))(\d{7})$/);
}, "Inserisci un numero di cellulare valido");