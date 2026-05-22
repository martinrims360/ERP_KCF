// ==================== GESTIÓN DE PRODUCTOS - KCF CORPORACIÓN ====================
// Archivo: static/js/gestion_productos.js

// Variables globales para los modales
let editModal, deleteModal;

// ==================== NOTIFICACIONES ====================
function mostrarNotificacion(mensaje, tipo) {
    const div = document.createElement('div');
    div.className = `alert alert-${tipo} notificacion`;
    div.innerHTML = `<i class="bi bi-${tipo === 'success' ? 'check-circle' : tipo === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>${mensaje}`;
    div.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    document.body.appendChild(div);
    setTimeout(() => {
        div.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => div.remove(), 300);
    }, 3000);
}

// ==================== CARGAR PRODUCTOS EN LOS SELECTS ====================
async function cargarProductos() {
    console.log("🟢 Cargando productos en selects...");
    try {
        const res = await fetch('/api/productos');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        const productos = await res.json();
        console.log(`📦 ${productos.length} productos cargados`);
        
        // Llenar select del kárdex
        const selectKardex = document.getElementById('kardex_producto_id');
        if (selectKardex) {
            selectKardex.innerHTML = '<option value="">Seleccione un producto</option>';
            productos.forEach(p => {
                const descripcion = p.descripcion ? p.descripcion.substring(0, 50) : 'Sin descripción';
                selectKardex.innerHTML += `<option value="${p.id}">${p.codigo || 'Sin código'} - ${descripcion} (Stock: ${p.stock || 0})</option>`;
            });
        }
        
        // Llenar select de nuevo movimiento
        const selectMov = document.getElementById('mov_kardex_producto_id');
        if (selectMov) {
            selectMov.innerHTML = '<option value="">Seleccione un producto</option>';
            productos.forEach(p => {
                const descripcion = p.descripcion ? p.descripcion.substring(0, 50) : 'Sin descripción';
                selectMov.innerHTML += `<option value="${p.id}">${p.codigo || 'Sin código'} - ${descripcion}</option>`;
            });
        }
        
        console.log("✅ Productos cargados exitosamente");
    } catch (e) {
        console.error("❌ Error al cargar productos:", e);
        mostrarNotificacion("Error al cargar productos: " + e.message, "danger");
    }
}

// ==================== FUNCIONES KÁRDEX ====================

// Cargar movimientos del kárdex
async function cargarKardex(productoId) {
    const tbody = document.getElementById('tbody-kardex');
    if (!productoId) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">Seleccione un producto</td></tr>';
        document.getElementById('kardex_stock_actual').textContent = '0';
        document.getElementById('kardex_valor_total').textContent = 'S/ 0.00';
        return;
    }
    
    tbody.innerHTML = '<tr><td colspan="8" class="text-center"><div class="spinner-border spinner-border-sm me-2"></div>Cargando...</td></tr>';
    
    try {
        const res = await fetch(`/api/movimientos_stock?producto_id=${productoId}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        const movimientos = await res.json();
        console.log(`📊 ${movimientos.length} movimientos encontrados`);
        
        if (movimientos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center">No hay movimientos para este producto</td></tr>';
            await actualizarStockProducto(productoId);
            return;
        }
        
        tbody.innerHTML = '';
        let saldo = 0;
        
        movimientos.forEach(mov => {
            if (mov.tipo === 'ENTRADA') saldo += mov.cantidad;
            else if (mov.tipo === 'SALIDA') saldo -= mov.cantidad;
            else if (mov.tipo === 'AJUSTE') saldo = mov.cantidad;
            
            const fecha = mov.created_at ? new Date(mov.created_at).toLocaleDateString('es-PE') : '-';
            
            tbody.innerHTML += `
                <tr>
                    <td>${fecha}</td>
                    <td><span class="badge ${mov.tipo === 'ENTRADA' ? 'bg-success' : mov.tipo === 'SALIDA' ? 'bg-danger' : 'bg-warning'}">${mov.tipo}</span></td>
                    <td>${mov.referencia || '-'}</td>
                    <td>${mov.motivo || '-'}</td>
                    <td class="text-end text-success">${mov.tipo === 'ENTRADA' ? mov.cantidad : '-'}</td>
                    <td class="text-end text-danger">${mov.tipo === 'SALIDA' ? mov.cantidad : '-'}</td>
                    <td class="text-end fw-bold">${saldo}</td>
                    <td class="text-end">${mov.costo_unitario ? 'S/ ' + mov.costo_unitario.toFixed(2) : '-'}</td>
                </tr>
            `;
        });
        
        document.getElementById('kardex_stock_actual').textContent = saldo;
        await actualizarValorTotal(productoId, saldo);
        
    } catch (e) {
        console.error("❌ Error al cargar kárdex:", e);
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Error: ${e.message}</td></tr>`;
        mostrarNotificacion("Error al cargar kárdex", "danger");
    }
}

async function actualizarStockProducto(productoId) {
    try {
        const res = await fetch(`/api/productos/${productoId}`);
        if (res.ok) {
            const p = await res.json();
            document.getElementById('kardex_stock_actual').textContent = p.stock || 0;
            await actualizarValorTotal(productoId, p.stock || 0);
        }
    } catch (e) {
        console.error("Error actualizando stock:", e);
    }
}

async function actualizarValorTotal(productoId, stock) {
    try {
        const res = await fetch(`/api/productos/${productoId}`);
        if (res.ok) {
            const p = await res.json();
            const valor = stock * (p.costo_unitario || 0);
            document.getElementById('kardex_valor_total').textContent = `S/ ${valor.toFixed(2)}`;
        }
    } catch (e) {
        console.error("Error actualizando valor total:", e);
    }
}

// Guardar nuevo movimiento
async function guardarMovimiento() {
    const productoId = document.getElementById('mov_kardex_producto_id').value;
    const tipo = document.getElementById('mov_kardex_tipo').value;
    const cantidad = document.getElementById('mov_kardex_cantidad').value;
    const costo = document.getElementById('mov_kardex_costo').value;
    const referencia = document.getElementById('mov_kardex_referencia').value;
    const motivo = document.getElementById('mov_kardex_motivo').value;
    
    if (!productoId) {
        mostrarNotificacion("Seleccione un producto", "warning");
        return;
    }
    if (!cantidad || cantidad <= 0) {
        mostrarNotificacion("Cantidad válida requerida", "warning");
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
    
    const btn = document.getElementById('btnGuardarMovimientoKardex');
    const textoOriginal = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
    
    try {
        const res = await fetch('/api/movimientos_stock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        
        const result = await res.json();
        
        if (res.ok && result.success) {
            mostrarNotificacion("✅ Movimiento registrado correctamente", "success");
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoMovimientoKardex'));
            if (modal) modal.hide();
            
            // Recargar kárdex
            const select = document.getElementById('kardex_producto_id');
            if (select && select.value) {
                await cargarKardex(select.value);
            }
            
            // Limpiar formulario
            document.getElementById('mov_kardex_cantidad').value = '';
            document.getElementById('mov_kardex_costo').value = '';
            document.getElementById('mov_kardex_referencia').value = '';
            document.getElementById('mov_kardex_motivo').value = '';
            
            // Recargar productos
            await cargarProductos();
            
            // Recargar página después de 1.5 segundos
            setTimeout(() => location.reload(), 1500);
        } else {
            mostrarNotificacion("❌ " + (result.error || "Error al registrar movimiento"), "danger");
        }
    } catch (e) {
        console.error("Error guardando movimiento:", e);
        mostrarNotificacion("❌ Error de conexión al servidor", "danger");
    } finally {
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    }
}

// ==================== FUNCIONES PARA EDITAR PRODUCTO ====================

function abrirModalEdicion(productoId) {
    console.log("✏️ Abriendo edición para producto ID:", productoId);
    
    const btnEditar = document.querySelector(`.btn-editar-producto[data-id="${productoId}"]`);
    if (!btnEditar) {
        console.error("No se encontró el botón de editar");
        mostrarNotificacion("Error: No se encontraron datos del producto", "danger");
        return;
    }
    
    // Llenar el formulario de edición
    document.getElementById('edit_id').value = btnEditar.dataset.id || '';
    document.getElementById('edit_familia').value = btnEditar.dataset.familia || '';
    document.getElementById('edit_descripcion').value = btnEditar.dataset.descripcion || '';
    document.getElementById('edit_descripcion_larga').value = btnEditar.dataset.descripcion_larga || '';
    document.getElementById('edit_marca').value = btnEditar.dataset.marca || '';
    document.getElementById('edit_modelo').value = btnEditar.dataset.modelo || '';
    document.getElementById('edit_unidad').value = btnEditar.dataset.unidad || '';
    document.getElementById('edit_volumen').value = btnEditar.dataset.volumen || '';
    document.getElementById('edit_observaciones').value = btnEditar.dataset.observaciones || '';
    document.getElementById('edit_transporte').value = btnEditar.dataset.transporte || '';
    document.getElementById('edit_costo_unitario').value = btnEditar.dataset.costo_unitario || '';
    document.getElementById('edit_precio_unitario').value = btnEditar.dataset.precio_unitario || '';
    document.getElementById('edit_stock').value = btnEditar.dataset.stock || '';
    
    calcularMargenEdicion();
    
    if (editModal) {
        editModal.show();
    } else {
        console.error("Modal de edición no inicializado");
        mostrarNotificacion("Error: Modal de edición no disponible", "danger");
    }
}

function calcularMargenEdicion() {
    const costo = parseFloat(document.getElementById('edit_costo_unitario').value) || 0;
    const precio = parseFloat(document.getElementById('edit_precio_unitario').value) || 0;
    
    if (costo > 0 && precio > 0) {
        const margen = ((precio - costo) / costo * 100).toFixed(2);
        document.getElementById('edit_margen').value = margen;
    } else {
        document.getElementById('edit_margen').value = '';
    }
}

async function guardarEdicion() {
    const id = document.getElementById('edit_id').value;
    
    if (!id) {
        mostrarNotificacion("Error: ID de producto no encontrado", "danger");
        return;
    }
    
    const datos = {
        familia: document.getElementById('edit_familia').value,
        descripcion: document.getElementById('edit_descripcion').value,
        descripcion_larga: document.getElementById('edit_descripcion_larga').value,
        marca: document.getElementById('edit_marca').value,
        modelo: document.getElementById('edit_modelo').value,
        unidad: document.getElementById('edit_unidad').value,
        volumen: document.getElementById('edit_volumen').value,
        observaciones: document.getElementById('edit_observaciones').value,
        transporte: document.getElementById('edit_transporte').value,
        costo_unitario: parseFloat(document.getElementById('edit_costo_unitario').value) || 0,
        precio_unitario: parseFloat(document.getElementById('edit_precio_unitario').value) || 0,
        stock: parseInt(document.getElementById('edit_stock').value) || 0
    };
    
    const btn = document.getElementById('btnGuardarEdicionProducto');
    const textoOriginal = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
    
    try {
        const response = await fetch('/api/productos/' + id, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            mostrarNotificacion("✅ Producto actualizado correctamente", "success");
            if (editModal) editModal.hide();
            setTimeout(() => location.reload(), 1000);
        } else {
            mostrarNotificacion("❌ Error: " + (result.error || "No se pudo actualizar"), "danger");
        }
    } catch (error) {
        console.error("Error al guardar edición:", error);
        mostrarNotificacion("❌ Error de conexión al servidor", "danger");
    } finally {
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    }
}

// ==================== FUNCIONES PARA ELIMINAR PRODUCTO ====================

function abrirModalEliminacion(productoId, descripcion) {
    console.log("🗑️ Abriendo eliminación para producto:", productoId);
    
    document.getElementById('eliminar_id_producto').value = productoId;
    document.getElementById('textoProductoEliminar').textContent = descripcion || 'Producto sin descripción';
    
    if (deleteModal) {
        deleteModal.show();
    } else {
        console.error("Modal de eliminación no inicializado");
        mostrarNotificacion("Error: Modal de eliminación no disponible", "danger");
    }
}

async function eliminarProducto() {
    const id = document.getElementById('eliminar_id_producto').value;
    
    if (!id) {
        mostrarNotificacion("Error: ID de producto no encontrado", "danger");
        return;
    }
    
    const btn = document.getElementById('btnConfirmarEliminarProducto');
    const textoOriginal = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Eliminando...';
    
    try {
        const response = await fetch('/api/productos/' + id, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            mostrarNotificacion("✅ Producto eliminado correctamente", "success");
            if (deleteModal) deleteModal.hide();
            setTimeout(() => location.reload(), 1000);
        } else {
            mostrarNotificacion("❌ Error: " + (result.error || "No se pudo eliminar"), "danger");
        }
    } catch (error) {
        console.error("Error al eliminar producto:", error);
        mostrarNotificacion("❌ Error de conexión al servidor", "danger");
    } finally {
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    }
}

// ==================== FILTROS Y BÚSQUEDA ====================

function aplicarFiltros() {
    const familia = document.getElementById('filtro-familia').value;
    const busqueda = document.getElementById('filtro-busqueda').value.toLowerCase();
    const filas = document.querySelectorAll('#tbody-productos tr');
    
    let contadorVisibles = 0;
    
    filas.forEach(fila => {
        let mostrar = true;
        
        if (familia) {
            const familiaProducto = fila.getAttribute('data-familia');
            if (familiaProducto !== familia) {
                mostrar = false;
            }
        }
        
        if (mostrar && busqueda) {
            const textoBusqueda = fila.getAttribute('data-codigo') + ' ' + fila.getAttribute('data-descripcion');
            if (!textoBusqueda.toLowerCase().includes(busqueda)) {
                mostrar = false;
            }
        }
        
        fila.style.display = mostrar ? '' : 'none';
        if (mostrar) contadorVisibles++;
    });
    
    const contador = document.querySelector('.form-control.bg-light.fw-bold.text-primary');
    if (contador) {
        contador.textContent = contadorVisibles + ' productos';
    }
}

// ==================== IMPORTAR EXCEL ====================

function configurarImportacion() {
    const btnImportar = document.getElementById('btnImportar');
    const fileInput = document.getElementById('fileInput');
    
    if (btnImportar && fileInput) {
        btnImportar.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                const form = btnImportar.closest('form');
                if (form) {
                    form.submit();
                }
            }
        });
    }
}

// ==================== MARGEN EN NUEVO PRODUCTO ====================

function configurarCalculoMargen() {
    const costoInput = document.getElementById('costo_unitario');
    const precioInput = document.getElementById('precio_unitario');
    const margenInput = document.getElementById('margen');
    
    if (!costoInput || !precioInput || !margenInput) return;
    
    function calcularMargen() {
        const costo = parseFloat(costoInput.value) || 0;
        const precio = parseFloat(precioInput.value) || 0;
        
        if (costo > 0 && precio > 0) {
            const margen = ((precio - costo) / costo * 100).toFixed(2);
            margenInput.value = margen;
        } else {
            margenInput.value = '';
        }
    }
    
    costoInput.addEventListener('input', calcularMargen);
    precioInput.addEventListener('input', calcularMargen);
}

// ==================== CONFIGURAR PESO ====================

function configurarPeso() {
    const tipoPeso = document.getElementById('tipo_peso');
    const contenedorRango = document.getElementById('contenedor-rango');
    const contenedorExacto = document.getElementById('contenedor-exacto');
    
    if (tipoPeso && contenedorRango && contenedorExacto) {
        tipoPeso.addEventListener('change', () => {
            if (tipoPeso.value === 'rango') {
                contenedorRango.style.display = 'block';
                contenedorExacto.style.display = 'none';
            } else {
                contenedorRango.style.display = 'none';
                contenedorExacto.style.display = 'block';
            }
        });
    }
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log("🟢 Inicializando sistema de gestión de productos...");
    
    // Inicializar modales
    const modalEditarElement = document.getElementById('modalEditarProducto');
    const modalEliminarElement = document.getElementById('modalEliminarProducto');
    
    if (modalEditarElement) {
        editModal = new bootstrap.Modal(modalEditarElement);
        console.log("✅ Modal de edición inicializado");
    }
    
    if (modalEliminarElement) {
        deleteModal = new bootstrap.Modal(modalEliminarElement);
        console.log("✅ Modal de eliminación inicializado");
    }
    
    // Cargar productos
    cargarProductos();
    
    // Delegación de eventos para botones
    document.body.addEventListener('click', (e) => {
        const btnEditar = e.target.closest('.btn-editar-producto');
        if (btnEditar) {
            e.preventDefault();
            const productoId = btnEditar.getAttribute('data-id');
            if (productoId) abrirModalEdicion(productoId);
            return;
        }
        
        const btnEliminar = e.target.closest('.btn-eliminar-producto');
        if (btnEliminar) {
            e.preventDefault();
            const productoId = btnEliminar.getAttribute('data-id');
            const descripcion = btnEliminar.getAttribute('data-descripcion');
            if (productoId) abrirModalEliminacion(productoId, descripcion);
            return;
        }
    });
    
    // Modal Kárdex
    const modalKardex = document.getElementById('modalKardex');
    if (modalKardex) {
        modalKardex.addEventListener('shown.bs.modal', () => {
            const select = document.getElementById('kardex_producto_id');
            if (select && select.value) {
                cargarKardex(select.value);
            }
        });
    }
    
    // Filtro kárdex
    const filtroKardex = document.getElementById('kardex_producto_id');
    if (filtroKardex) {
        filtroKardex.addEventListener('change', (e) => {
            cargarKardex(e.target.value);
        });
    }
    
    // Botón guardar movimiento
    const btnGuardarMovimiento = document.getElementById('btnGuardarMovimientoKardex');
    if (btnGuardarMovimiento) {
        btnGuardarMovimiento.addEventListener('click', guardarMovimiento);
    }
    
    // Botón guardar edición
    const btnGuardarEdicion = document.getElementById('btnGuardarEdicionProducto');
    if (btnGuardarEdicion) {
        btnGuardarEdicion.addEventListener('click', guardarEdicion);
    }
    
    // Botón confirmar eliminación
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminarProducto');
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', eliminarProducto);
    }
    
    // Calcular margen en edición
    const editCosto = document.getElementById('edit_costo_unitario');
    const editPrecio = document.getElementById('edit_precio_unitario');
    if (editCosto && editPrecio) {
        editCosto.addEventListener('input', calcularMargenEdicion);
        editPrecio.addEventListener('input', calcularMargenEdicion);
    }
    
    // Filtros de tabla
    const filtroFamilia = document.getElementById('filtro-familia');
    const filtroBusqueda = document.getElementById('filtro-busqueda');
    if (filtroFamilia) filtroFamilia.addEventListener('change', aplicarFiltros);
    if (filtroBusqueda) filtroBusqueda.addEventListener('keyup', aplicarFiltros);
    
    // Configurar importación
    configurarImportacion();
    configurarCalculoMargen();
    configurarPeso();
    
    // Fecha por defecto
    const fechaInput = document.getElementById('mov_kardex_fecha');
    if (fechaInput) {
        fechaInput.value = new Date().toISOString().split('T')[0];
    }
    
    console.log("✅ Inicialización completa");
});