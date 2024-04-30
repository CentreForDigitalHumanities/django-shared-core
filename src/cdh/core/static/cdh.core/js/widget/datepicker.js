$(function() {
    const elem = document.querySelector('.bootstrap-datepicker');
    const datepicker = new Datepicker(elem, {
        buttonClass: 'btn',
        format: 'dd-mm-yyyy',
    });
});