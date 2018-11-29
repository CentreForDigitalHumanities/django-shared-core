function depends_on_value(a, a_value, b)
{
    $('input[name=' + a + ']').change(function() {
        var check = $('input[name=' + a + ']:checked').val() === a_value;

        $('#id_' + b).parents('tr').toggle(check);
    });
    $('input[name=' + a + ']').change();
}
