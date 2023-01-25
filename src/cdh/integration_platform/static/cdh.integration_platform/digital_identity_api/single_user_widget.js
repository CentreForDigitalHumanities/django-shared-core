$(function () {
    $('.dia-single-user').keyup((e) => {
        var testEmail = /^[A-Z0-9._%+-]+@(acc\.)?uu\.nl$/i;
        console.log($(e.target), $(e.target).val(), testEmail.test($(e.target).val()))
    })
})
