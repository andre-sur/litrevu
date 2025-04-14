document.addEventListener('DOMContentLoaded', function() {
    const toggleButtons = document.querySelectorAll('.toggle-details');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            const detailsDiv = document.getElementById('details-' + reviewId);

            if (detailsDiv.style.display === 'none') {
                detailsDiv.style.display = 'block';
                this.textContent = 'Masquer les détails';
            } else {
                detailsDiv.style.display = 'none';
                this.textContent = 'Voir les détails';
            }
        });
    });
});
