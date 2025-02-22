function search() {
    const query = document.getElementById('search-input').value;
    if (query) {
        window.location.href = '/search?query=' + encodeURIComponent(query);
    }
} 