// gestion_productos.js - VERSIÓN COMPLETA Y FUNCIONAL

const filtroFamilia = document.getElementById('filtro-familia');
const filtroBusqueda = document.getElementById('filtro-busqueda');

if (filtroFamilia) {
    filtroFamilia.addEventListener('change', filtrarProductos);
}
if (filtroBusqueda) {
    filtroBusqueda.addEventListener('input', filtrarProductos);
}

function filtrarProductos() {
    const familia = filtroFamilia ? filtroFamilia.value.toLowerCase() : '';
    const busqueda = filtroBusqueda ? filtroBusqueda.value.toLowerCase() : '';
    const filas = document.querySelectorAll('#tabla-productos tbody tr');

    filas.forEach(fila => {
        const filaFamilia = (fila.dataset.familia || '').toLowerCase();
        const filaTexto = (fila.dataset.descripcion || '').toLowerCase();
        const filaCodigo = (fila.dataset.codigo || '').toLowerCase();
        const coincideFamilia = !familia || filaFamilia.includes(familia);
        const coincideBusqueda = !busqueda || filaTexto.includes(busqueda) || filaCodigo.includes(busqueda);
        fila.style.display = (coincideFamilia && coincideBusqueda) ? '' : 'none';
    });
}

// =====================================================
// CÁLCULO AUTOMÁTICO DE MARGEN
// =====================================================
function inicializarCalculoMargen() {
    // Modal Nuevo
    const costoNuevo = document.getElementById('costo_unitario');
    const precioNuevo = document.getElementById('precio_unitario');
    const margenNuevo = document.getElementById('margen');

    if (costoNuevo && precioNuevo && margenNuevo) {
        function calcularNuevo() {
            const costo = parseFloat(costoNuevo.value) || 0;
            const precio = parseFloat(precioNuevo.value) || 0;
            if (costo > 0) {
                margenNuevo.value = ((precio - costo) / costo * 100).toFixed(2);
            } else {
                margenNuevo.value = '';
            }
        }
        costoNuevo.addEventListener('input', calcularNuevo);
        precioNuevo.addEventListener('input', calcularNuevo);
    }

    // Modal Editar
    const costoEdit = document.getElementById('edit_costo_unitario');
    const precioEdit = document.getElementById('edit_precio_unitario');
    const margenEdit = document.getElementById('edit_margen');

    if (costoEdit && precioEdit && margenEdit) {
        function calcularEdit() {
            const costo = parseFloat(costoEdit.value) || 0;
            const precio = parseFloat(precioEdit.value) || 0;
            if (costo > 0) {
                margenEdit.value = ((precio - costo) / costo * 100).toFixed(2);
            } else {
                margenEdit.value = '';
            }
        }
        costoEdit.addEventListener('input', calcularEdit);
        precioEdit.addEventListener('input', calcularEdit);
    }
}

// =====================================================
// INICIALIZACIÓN
// =====================================================
document.addEventListener('DOMContentLoaded', () => {
    inicializarCalculoMargen();

    const modalNuevo = document.getElementById('modalNuevoProducto');
    if (modalNuevo) {
        modalNuevo.addEventListener('shown.bs.modal', () => inicializarCalculoMargen());
    }

    const modalEditar = document.getElementById('modalEditarProducto');
    if (modalEditar) {
        modalEditar.addEventListener('shown.bs.modal', () => inicializarCalculoMargen());
    }

    // IMPORTAR EXCEL
    const btnImportar = document.getElementById('btnImportar');
    const fileInput = document.getElementById('fileInput');
    if (btnImportar && fileInput) {
        btnImportar.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) this.closest('form').submit();
        });
    }

    // SELECT2
    $(document).ready(function() {
        $('#familia').select2({ dropdownParent: $('#modalNuevoProducto'), placeholder: "Buscar familia..." });
        $('#marca').select2({ dropdownParent: $('#modalNuevoProducto'), placeholder: "Buscar marca..." });
        $('#unidad').select2({ dropdownParent: $('#modalNuevoProducto'), placeholder: "Buscar unidad..." });
    });

    // CAMBIO PESO
    const tipoPeso = document.getElementById('tipo_peso');
    if (tipoPeso) {
        tipoPeso.addEventListener('change', function() {
            const rango = document.getElementById('contenedor-rango');
            const exacto = document.getElementById('contenedor-exacto');
            if (this.value === 'exacto') {
                if (rango) rango.style.display = 'none';
                if (exacto) exacto.style.display = 'block';
            } else {
                if (rango) rango.style.display = 'block';
                if (exacto) exacto.style.display = 'none';
            }
        });
    }

    // DELEGACIÓN DE EVENTOS PARA EDITAR Y ELIMINAR
    const tbody = document.getElementById('tbody-productos');
    if (tbody) {
        tbody.addEventListener('click', function(e) {
            const btnEditar = e.target.closest('.btn-editar-producto');
            if (btnEditar) {
                editarProducto(btnEditar);
                return;
            }
            const btnEliminar = e.target.closest('.btn-eliminar-producto');
            if (btnEliminar) {
                eliminarProducto(btnEliminar);
                return;
            }
        });
    }

    // BOTÓN GUARDAR EDICIÓN
    const btnGuardar = document.getElementById('btnGuardarEdicionProducto');
    if (btnGuardar) {
        btnGuardar.addEventListener('click', guardarEdicionProducto);
    }

    // ✅ BOTÓN CONFIRMAR ELIMINACIÓN - ESTO ES LO QUE TE FALTABA
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminarProducto');
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', confirmarEliminarProducto);
    }
});

// =====================================================
// EDITAR PRODUCTO
// =====================================================
function editarProducto(btn) {
    const campos = {
        edit_id: btn.dataset.id,
        edit_familia: btn.dataset.familia,
        edit_marca: btn.dataset.marca,
        edit_descripcion: btn.dataset.descripcion,
        edit_modelo: btn.dataset.modelo,
        edit_unidad: btn.dataset.unidad,
        edit_volumen: btn.dataset.volumen,
        edit_transporte: btn.dataset.transporte,
        edit_observaciones: btn.dataset.observaciones,
        edit_descripcion_larga: btn.dataset.descripcion_larga,
        edit_costo_unitario: btn.dataset.costo_unitario,
        edit_precio_unitario: btn.dataset.precio_unitario,
        edit_stock: btn.dataset.stock
    };

    for (const id in campos) {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.value = campos[id] || '';
        }
    }

    const modal = new bootstrap.Modal(document.getElementById('modalEditarProducto'));
    modal.show();
}

// =====================================================
// GUARDAR EDICIÓN - CORREGIDO
// =====================================================
async function guardarEdicionProducto() {
    const id = document.getElementById('edit_id').value;
    if (!id) {
        mostrarNotificacion("❌ No se encontró el ID", "danger");
        return;
    }

    const datos = {
        familia: document.getElementById('edit_familia').value,
        marca: document.getElementById('edit_marca').value,
        descripcion: document.getElementById('edit_descripcion').value,
        modelo: document.getElementById('edit_modelo').value,
        unidad: document.getElementById('edit_unidad').value,
        volumen: document.getElementById('edit_volumen').value,
        transporte: document.getElementById('edit_transporte').value,
        observaciones: document.getElementById('edit_observaciones').value,
        descripcion_larga: document.getElementById('edit_descripcion_larga').value,
        costo_unitario: parseFloat(document.getElementById('edit_costo_unitario').value) || 0,
        precio_unitario: parseFloat(document.getElementById('edit_precio_unitario').value) || 0,
        stock: parseInt(document.getElementById('edit_stock').value) || 0
    };

    try {
        const response = await fetch(`/api/productos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });

        const result = await response.json();

        if (result.success) {
            mostrarNotificacion("✅ Producto actualizado correctamente", "success");
            bootstrap.Modal.getInstance(document.getElementById('modalEditarProducto')).hide();
            // ✅ RECARGAR LA PÁGINA PARA VER LOS CAMBIOS
            setTimeout(() => location.reload(), 800);
        } else {
            mostrarNotificacion("❌ Error: " + (result.error || "Error desconocido"), "danger");
        }
    } catch (error) {
        console.error(error);
        mostrarNotificacion("❌ Error de conexión", "danger");
    }
}

// =====================================================
// ELIMINAR PRODUCTO - ABRIR MODAL
// =====================================================
function eliminarProducto(btn) {
    const id = btn.dataset.id;
    const descripcion = btn.dataset.descripcion || 'Producto';

    document.getElementById('eliminar_id_producto').value = id;
    document.getElementById('textoProductoEliminar').textContent = descripcion;

    const modal = new bootstrap.Modal(document.getElementById('modalEliminarProducto'));
    modal.show();
}

// =====================================================
// ✅ CONFIRMAR ELIMINAR PRODUCTO - ESTA FUNCIÓN ES LA QUE TE FALTABA
// =====================================================
async function confirmarEliminarProducto() {
    const id = document.getElementById('eliminar_id_producto').value;

    if (!id) {
        mostrarNotificacion("❌ No se encontró el ID del producto", "danger");
        return;
    }

    try {
        const response = await fetch(`/api/productos/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const result = await response.json();

        if (result.success) {
            mostrarNotificacion("✅ Producto eliminado correctamente", "success");
            bootstrap.Modal.getInstance(document.getElementById('modalEliminarProducto')).hide();
            // ✅ RECARGAR LA PÁGINA PARA VER LOS CAMBIOS
            setTimeout(() => location.reload(), 800);
        } else {
            mostrarNotificacion("❌ Error al eliminar: " + (result.error || "Error desconocido"), "danger");
        }
    } catch (error) {
        console.error(error);
        mostrarNotificacion("❌ Error de conexión", "danger");
    }
}

// =====================================================
// NOTIFICACIONES
// =====================================================
function mostrarNotificacion(mensaje, tipo) {
    const notificacion = document.createElement('div');
    notificacion.className = `alert alert-${tipo} position-fixed top-0 end-0 m-3`;
    notificacion.style.zIndex = '10000';
    notificacion.style.minWidth = '300px';
    notificacion.style.animation = 'slideIn 0.3s ease';
    
    const icono = tipo === 'success' ? 'check-circle' : (tipo === 'danger' ? 'exclamation-triangle' : 'info-circle');
    notificacion.innerHTML = `<i class="bi bi-${icono} me-2"></i>${mensaje}`;
    
    document.body.appendChild(notificacion);
    
    setTimeout(() => {
        notificacion.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notificacion.remove(), 300);
    }, 3000);
}

// ESTILOS
if (!document.querySelector('#notificaciones-styles')) {
    const style = document.createElement('style');
    style.id = 'notificaciones-styles';
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}