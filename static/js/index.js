document.addEventListener("DOMContentLoaded", function() {

    console.log('✅ Sistema cargado correctamente');

    const nombre = document.body.dataset.nombre;
    const rol = document.body.dataset.rol;

    console.log('Usuario:', nombre);
    console.log('Rol:', rol);

    // Función reutilizable
    function aplicarHover(elemento, enterStyle, leaveStyle) {
        elemento.addEventListener('mouseenter', () => {
            Object.assign(elemento.style, enterStyle);
        });

        elemento.addEventListener('mouseleave', () => {
            Object.assign(elemento.style, leaveStyle);
        });
    }

    // Botones
    document.querySelectorAll('.boton').forEach(boton => {
        aplicarHover(
            boton,
            { transform: 'translateY(-5px) scale(1.02)' },
            { transform: 'translateY(0) scale(1)' }
        );
    });

    // User info
    const userInfo = document.querySelector('.user-info');

    if (userInfo) {
        aplicarHover(
            userInfo,
            {
                transform: 'scale(1.05)',
                boxShadow: '0 4px 15px rgba(0,0,0,0.3)'
            },
            {
                transform: 'scale(1)',
                boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
            }
        );
    }

});