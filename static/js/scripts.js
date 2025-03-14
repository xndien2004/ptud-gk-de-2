// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Initialize popovers
    $('[data-toggle="popover"]').popover();

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirm delete actions
    $('.delete-confirm').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });

    // Handle form validation
    $('form').on('submit', function() {
        $(this).find(':input').filter(function() {
            return !this.value;
        }).closest('.form-group').addClass('has-error');
    });

    // Remove error class on input
    $('.form-group input').on('input', function() {
        $(this).closest('.form-group').removeClass('has-error');
    });
});
