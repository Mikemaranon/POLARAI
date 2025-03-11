document.getElementById('theme-toggle-checkbox').addEventListener('change', function() {
    const themeStyle = document.getElementById('theme-style');
    if (this.checked) {
        themeStyle.setAttribute('href', "/static/style/dark-theme.css");
    } else {
        themeStyle.setAttribute('href', "/static/style/bright-theme.css");
    }
});
