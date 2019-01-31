function depends_on_value(a, a_value, b)
{
    $('input[name=' + a + ']').change(function() {
        let check = $('input[name=' + a + ']:checked').val() === a_value;

        $('#id_' + b).parents('tr').toggle(check);
    });
    $('input[name=' + a + ']').change();
}

function add_title(field, title)
{
    let insert = $('<tr class="no-background">').append($('<th>').append($('<h3>').text(title))).append($('<td>'));
    $('#id_' + field).parents('tr').before(insert);
    console.log("#id_"+field)
}