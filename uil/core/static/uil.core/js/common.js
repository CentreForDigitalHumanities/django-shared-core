$(function() {
    // Turns al tables with the dt class into datatable tables
    $('table.dt').DataTable( {
        dom: 'Bfrtip',
        buttons : [
            'copyHtml5',
            'csvHtml5',
            'pdfHtml5',
            'print',
            'pageLength'
        ],
        lengthMenu: [
            [10, 20, 50, -1],
            ["10", "20", "50", "\u221e"]
        ],
        responsive: true,
        paginationType: "full_numbers",
    } );

    // Enables select2 for all select boxes in forms
    $('form table select').select2();

    // Turns all help text into nice (i) icons with qTip hover-text
    $("[id^=id]").each(function() {
        let help = $(this).nextAll('.helptext');
        if (help.html())
        {
            let label = $("th label[for^='" + $(this).attr('id') + "']").first();
            let icon = $('<span class="icon-info"></span');
            icon.html('&nbsp;');
            icon.appendTo(label);
            icon.qtip({
                content: {
                    text: help.html(),
                },
                hide: {
                    fixed: true,
                    delay: 500,
                },
            });
            help.remove();
        }
    });
});
