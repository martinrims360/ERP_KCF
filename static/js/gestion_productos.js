// gestion_productos.js - VERSIÓN COMPLETA Y FUNCIONAL CON KÁRDEX

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
// KÁRDEX - FUNCIONES CORREGIDAS
// =====================================================

// Cargar productos en el select del kárdex
async function cargarProductosKardex() {
    console.log("🟢 Cargando productos para kárdex...");
    const selects = [
        document.getElementById('kardex_producto_id'),
        document.getElementById('mov_kardex_producto_id')
    ];

    try {
        const res = await fetch('/api/productos');
        console.log("📡 Respuesta del servidor:", res.status);
        
        if (!res.ok) {
            throw new Error(`Error HTTP: ${res.status}`);
        }
        
        const productos = await res.json();
        console.log("📦 Productos recibidos:", productos.length);

        selects.forEach(select => {
            if (!select) return;
            select.innerHTML = '<option value="">Seleccione un producto</option>';
            if (productos.length === 0) {
                select.innerHTML += '<option value="" disabled>No hay productos disponibles</option>';
            } else {
                productos.forEach(p => {
                    select.innerHTML += `<option value="${p.id}">${p.codigo || 'Sin código'} - ${p.descripcion.substring(0, 50)}</option>`;
                });
            }
        });
        
        console.log("✅ Productos cargados exitosamente");
    } catch (e) {
        console.error("❌ Error cargando productos para Kárdex", e);
        mostrarNotificacion("Error al cargar productos para kárdex", "danger");
        
        selects.forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">Error al cargar productos</option>';
            }
        });
    }
}

// Cargar movimientos del kárdex
async function cargarKardex(productoId = '') {
    const tbody = document.getElementById('tbody-kardex');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4">Cargando movimientos...</td></tr>`;

    try {
        let url = '/api/movimientos_stock';
        if (productoId) url += `?producto_id=${productoId}`;

        const res = await fetch(url);
        console.log("📊 Respuesta movimientos:", res.status);
        
        if (!res.ok) {
            throw new Error(`Error HTTP: ${res.status}`);
        }
        
        const movimientos = await res.json();
        console.log("📊 Movimientos recibidos:", movimientos.length);

        tbody.innerHTML = '';
        let saldo = 0;

        if (movimientos.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4">No hay movimientos para este producto</td></tr>`;
        }

        movimientos.forEach(mov => {
            if (mov.tipo === 'ENTRADA') {
                saldo += parseInt(mov.cantidad);
            } else if (mov.tipo === 'SALIDA') {
                saldo -= parseInt(mov.cantidad);
            } else if (mov.tipo === 'AJUSTE') {
                saldo = parseInt(mov.cantidad);
            }

            const fecha = mov.created_at ? new Date(mov.created_at).toLocaleDateString('es-PE') : '-';
            
            const fila = `
                <tr>
                    <td>${fecha}</td>
                    <td>
                        <span class="badge ${mov.tipo === 'ENTRADA' ? 'bg-success' : mov.tipo === 'SALIDA' ? 'bg-danger' : 'bg-warning'}">
                            ${mov.tipo}
                        </span>
                    </td>
                    <td>${mov.referencia || '-'}</td>
                    <td>${mov.motivo || '-'}</td>
                    <td class="text-end text-success fw-bold">${mov.tipo === 'ENTRADA' ? mov.cantidad : '-'}</td>
                    <td class="text-end text-danger fw-bold">${mov.tipo === 'SALIDA' ? mov.cantidad : '-'}</td>
                    <td class="text-end fw-bold">${saldo}</td>
                    <td class="text-end">${mov.costo_unitario ? 'S/ ' + parseFloat(mov.costo_unitario).toFixed(2) : '-'}</td>
                </tr>`;
            tbody.innerHTML += fila;
        });

        // Actualizar stock actual
        document.getElementById('kardex_stock_actual').textContent = saldo;
        
        // Actualizar valor total (si hay costo unitario)
        if (movimientos.length > 0 && movimientos[0].costo_unitario) {
            const valorTotal = saldo * movimientos[0].costo_unitario;
            document.getElementById('kardex_valor_total').textContent = `S/ ${valorTotal.toFixed(2)}`;
        } else {
            document.getElementById('kardex_valor_total').textContent = 'S/ 0.00';
        }

    } catch (error) {
        console.error("❌ Error cargando kárdex:", error);
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Error al cargar el Kárdex: ${error.message}</td></tr>`;
        mostrarNotificacion("Error al cargar el kárdex", "danger");
    }
}

// Guardar nuevo movimiento
async function guardarMovimientoKardex() {
    console.log("🟢 Guardando movimiento...");
    
    const productoId = document.getElementById('mov_kardex_producto_id').value;
    const tipo = document.getElementById('mov_kardex_tipo').value;
    const cantidad = document.getElementById('mov_kardex_cantidad').value;
    const costo = document.getElementById('mov_kardex_costo').value;
    const referencia = document.getElementById('mov_kardex_referencia').value;
    const motivo = document.getElementById('mov_kardex_motivo').value;

    if (!productoId) {
        mostrarNotificacion("❌ Seleccione un producto", "danger");
        return;
    }
    
    if (!cantidad || parseInt(cantidad) <= 0) {
        mostrarNotificacion("❌ Ingrese una cantidad válida", "danger");
        return;
    }
    
    if (!tipo) {
        mostrarNotificacion("❌ Seleccione un tipo de movimiento", "danger");
        return;
    }

    const datos = {
        producto_id: parseInt(productoId),
        tipo: tipo,
        cantidad: parseInt(cantidad),
        costo_unitario: costo ? parseFloat(costo) : null,
        referencia: referencia || null,
        motivo: motivo || null
    };

    console.log("📝 Datos a enviar:", datos);

    try {
        const res = await fetch('/api/movimientos_stock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });

        console.log("📡 Respuesta del servidor:", res.status);
        const result = await res.json();
        console.log("📦 Respuesta:", result);

        if (res.ok && result.success) {
            mostrarNotificacion("✅ Movimiento registrado correctamente", "success");
            
            // Cerrar modal de nuevo movimiento
            const modalMovimiento = bootstrap.Modal.getInstance(document.getElementById('modalNuevoMovimientoKardex'));
            if (modalMovimiento) modalMovimiento.hide();
            
            // Recargar el kárdex
            const productoSelect = document.getElementById('kardex_producto_id');
            if (productoSelect && productoSelect.value) {
                await cargarKardex(productoSelect.value);
            } else {
                await cargarKardex();
            }
            
            // Limpiar formulario
            document.getElementById('mov_kardex_cantidad').value = '';
            document.getElementById('mov_kardex_costo').value = '';
            document.getElementById('mov_kardex_referencia').value = '';
            document.getElementById('mov_kardex_motivo').value = '';
            
            // Recargar productos para actualizar stock en tabla principal
            setTimeout(() => location.reload(), 1500);
        } else {
            mostrarNotificacion("❌ " + (result.error || "Error al registrar el movimiento"), "danger");
        }
    } catch (error) {
        console.error("❌ Error:", error);
        mostrarNotificacion("❌ Error de conexión al registrar movimiento", "danger");
    }
}

// =====================================================
// INICIALIZACIÓN
// =====================================================
document.addEventListener('DOMContentLoaded', () => {
    console.log("🟢 DOM cargado, inicializando...");
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

    // BOTÓN CONFIRMAR ELIMINACIÓN
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminarProducto');
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', confirmarEliminarProducto);
    }

    // ==================== KÁRDEX ====================
    console.log("🟢 Inicializando kárdex...");
    
    // Cargar productos al iniciar
    cargarProductosKardex();

    // Cuando se abre el modal del kárdex, cargar movimientos
    const modalKardex = document.getElementById('modalKardex');
    if (modalKardex) {
        modalKardex.addEventListener('shown.bs.modal', () => {
            console.log("🟢 Modal kárdex abierto");
            const productoSelect = document.getElementById('kardex_producto_id');
            if (productoSelect && productoSelect.value) {
                cargarKardex(productoSelect.value);
            } else {
                cargarKardex();
            }
        });
    }

    // Filtro por producto
    const filtroKardex = document.getElementById('kardex_producto_id');
    if (filtroKardex) {
        filtroKardex.addEventListener('change', () => {
            console.log("🟢 Filtro cambiado a:", filtroKardex.value);
            cargarKardex(filtroKardex.value);
        });
    }

    // Botón guardar movimiento
    const btnGuardarKardex = document.getElementById('btnGuardarMovimientoKardex');
    if (btnGuardarKardex) {
        btnGuardarKardex.addEventListener('click', guardarMovimientoKardex);
    }
    
    // Fecha por defecto en el modal de nuevo movimiento
    const fechaInput = document.getElementById('mov_kardex_fecha');
    if (fechaInput) {
        fechaInput.value = new Date().toISOString().split('T')[0];
    }
    
    console.log("✅ Inicialización completa");
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
// GUARDAR EDICIÓN
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
// ELIMINAR PRODUCTO
// =====================================================
function eliminarProducto(btn) {
    const id = btn.dataset.id;
    const descripcion = btn.dataset.descripcion || 'Producto';

    document.getElementById('eliminar_id_producto').value = id;
    document.getElementById('textoProductoEliminar').textContent = descripcion;

    const modal = new bootstrap.Modal(document.getElementById('modalEliminarProducto'));
    modal.show();
}

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
    notificacion.style.zIndex = '9999';
    
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