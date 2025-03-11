document.addEventListener('DOMContentLoaded', () => {
    const showPasswordBtn = document.getElementById('show-password');
    const passwordInput = document.querySelector('.password-container input');
    const deleteDataBtn = document.getElementById('delete-data');
    const modal = document.getElementById('confirm-modal');
    const confirmBtn = document.getElementById('confirm-delete');
    const cancelBtn = document.getElementById('cancel-delete');
    const themeSelect = document.getElementById('theme-select');

    // Mostrar/ocultar contraseña
    showPasswordBtn.addEventListener('click', () => {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
        } else {
            passwordInput.type = 'password';
        }
    });

    // Mostrar modal
    deleteDataBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
    });

    // Cerrar modal
    cancelBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Confirmar eliminación
    confirmBtn.addEventListener('click', () => {
        const password = document.getElementById('confirm-password').value;
        // Aquí iría la lógica de verificación de contraseña
        modal.style.display = 'none';
    });

    // Cambiar tema
    themeSelect.addEventListener('change', (e) => {
        const theme = e.target.value;
        // Aquí iría la lógica para cambiar el tema
    });
});