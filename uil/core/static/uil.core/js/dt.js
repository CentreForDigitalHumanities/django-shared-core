$(function() {
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
        language: {
            {% if LANGUAGE_CODE == 'nl' %}
                url: "{% static 'uil.core/js/datatables/lang/dutch.json' %}"
            {% else %}
                url: "{% static 'uil.core/js/datatables/lang/english.json' %}"
            {% endif %}
        }
    } );
});