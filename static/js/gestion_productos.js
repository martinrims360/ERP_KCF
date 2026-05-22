// ==================== FUNCIONES PARA PRODUCTOS Y KÁRDEX ====================

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
    `;
    document.body.appendChild(div);
    setTimeout(() => {
        div.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => div.remove(), 300);
    }, 3000);
}

// ==================== GESTIÓN DE PRODUCTOS ====================

// Cargar productos en los selects
async function cargarProductos() {
    console.log("🟢 Cargando productos...");
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
                selectKardex.innerHTML += `<option value="${p.id}">${p.codigo} - ${p.descripcion.substring(0, 50)} (Stock: ${p.stock})</option>`;
            });
        }
        
        // Llenar select de nuevo movimiento
        const selectMov = document.getElementById('mov_kardex_producto_id');
        if (selectMov) {
            selectMov.innerHTML = '<option value="">Seleccione un producto</option>';
            productos.forEach(p => {
                selectMov.innerHTML += `<option value="${p.id}">${p.codigo} - ${p.descripcion.substring(0, 50)}</option>`;
            });
        }
        
        console.log("✅ Productos cargados exitosamente");
    } catch (e) {
        console.error("❌ Error:", e);
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
    
    tbody.innerHTML = '<tr><td colspan="8" class="text-center">Cargando...</td></tr>';
    
    try {
        const res = await fetch(`/api/movimientos_stock?producto_id=${productoId}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        const movimientos = await res.json();
        console.log(`📊 ${movimientos.length} movimientos`);
        
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
        console.error("❌ Error:", e);
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
        console.error(e);
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
        console.error(e);
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
    btn.innerHTML = 'Guardando...';
    
    try {
        const res = await fetch('/api/movimientos_stock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        
        const result = await res.json();
        
        if (res.ok && result.success) {
            mostrarNotificacion("✅ Movimiento registrado", "success");
            
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
            
            // Recargar página
            setTimeout(() => location.reload(), 1000);
        } else {
            mostrarNotificacion("❌ " + (result.error || "Error"), "danger");
        }
    } catch (e) {
        console.error(e);
        mostrarNotificacion("❌ Error de conexión", "danger");
    } finally {
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    }
}

// ==================== FUNCIONES PARA EDITAR PRODUCTO ====================

// Función para abrir modal de edición
function abrirModalEdicion(productoId) {
    console.log("✏️ Abriendo edición para producto ID:", productoId);
    
    // Obtener los datos del producto desde los data attributes del botón
    const btnEditar = document.querySelector(`.btn-editar-producto[data-id="${productoId}"]`);
    if (!btnEditar) {
        console.error("No se encontró el botón de editar");
        mostrarNotificacion("Error: No se encontraron datos del producto", "danger");
        return;
    }
    
    // Llenar el formulario de edición con todos los datos
    document.getElementById('edit_id').value = btnEditar.dataset.id || '';
    document.getElementById('edit_familia').value = btnEditar.dataset.familia || '';
    document.getElementById('edit_descripcion').value = btnEditar.dataset.descripcion || '';
    document.getElementById('edit_descripcion_larga').value = btnEditar.dataset.descripcion_larga || '';
    document.getElementById('edit_marca').value = btnEditar.dataset.marca || '';
    document.getElementById('edit_modelo').value = btnEditar.dataset.modelo || '';
    document.getElementById('edit_unidad').value = btnEditar.dataset.unidad || '';
    
    // Manejar peso (puede ser rango o exacto)
    const peso = btnEditar.dataset.peso;
    if (peso) {
        // Verificar si existe el campo peso en el formulario
        const pesoInput = document.getElementById('edit_peso');
        if (pesoInput) pesoInput.value = peso;
    }
    
    document.getElementById('edit_volumen').value = btnEditar.dataset.volumen || '';
    document.getElementById('edit_observaciones').value = btnEditar.dataset.observaciones || '';
    document.getElementById('edit_transporte').value = btnEditar.dataset.transporte || '';
    document.getElementById('edit_costo_unitario').value = btnEditar.dataset.costo_unitario || '';
    document.getElementById('edit_precio_unitario').value = btnEditar.dataset.precio_unitario || '';
    document.getElementById('edit_stock').value = btnEditar.dataset.stock || '';
    
    // Calcular margen
    calcularMargenEdicion();
    
    // Mostrar modal
    if (editModal) {
        editModal.show();
    } else {
        console.error("Modal de edición no inicializado");
        mostrarNotificacion("Error: Modal de edición no disponible", "danger");
    }
}

// Función para calcular margen en edición
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

// Función para guardar edición
async function guardarEdicion() {
    const id = document.getElementById('edit_id').value;
    
    if (!id) {
        mostrarNotificacion("Error: ID de producto no encontrado", "danger");
        return;
    }
    
    const datos = {
        id: parseInt(id),
        familia: document.getElementById('edit_familia').value,
        descripcion: document.getElementById('edit_descripcion').value,
        descripcion_larga: document.getElementById('edit_descripcion_larga').value,
        marca: document.getElementById('edit_marca').value,
        modelo: document.getElementById('edit_modelo').value,
        unidad: document.getElementById('edit_unidad').value,
        peso: document.getElementById('edit_peso') ? document.getElementById('edit_peso').value : null,
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
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            mostrarNotificacion("✅ Producto actualizado correctamente", "success");
            
            // Cerrar modal
            if (editModal) editModal.hide();
            
            // Recargar la página para mostrar cambios
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

// Función para abrir modal de eliminación
function abrirModalEliminacion(productoId, descripcion) {
    console.log("🗑️ Abriendo eliminación para producto:", productoId, descripcion);
    
    document.getElementById('eliminar_id_producto').value = productoId;
    document.getElementById('textoProductoEliminar').textContent = descripcion || 'Producto sin descripción';
    
    if (deleteModal) {
        deleteModal.show();
    } else {
        console.error("Modal de eliminación no inicializado");
        mostrarNotificacion("Error: Modal de eliminación no disponible", "danger");
    }
}

// Función para eliminar producto
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
            
            // Cerrar modal
            if (deleteModal) deleteModal.hide();
            
            // Recargar después de 1 segundo
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
        
        // Filtrar por familia
        if (familia) {
            const familiaProducto = fila.getAttribute('data-familia');
            if (familiaProducto !== familia) {
                mostrar = false;
            }
        }
        
        // Filtrar por búsqueda
        if (mostrar && busqueda) {
            const textoBusqueda = fila.getAttribute('data-codigo') + ' ' + fila.getAttribute('data-descripcion');
            if (!textoBusqueda.toLowerCase().includes(busqueda)) {
                mostrar = false;
            }
        }
        
        fila.style.display = mostrar ? '' : 'none';
        if (mostrar) contadorVisibles++;
    });
    
    // Actualizar contador
    const contador = document.querySelector('.form-control.bg-light.fw-bold.text-primary');
    if (contador) {
        contador.textContent = contadorVisibles + ' productos';
    }
}

// ==================== IMPORTAR EXCEL ====================

function configurarImportacion() {
    const btnImportar = document.getElementById('btnImportar');
    const fileInput = document.getElementById('fileInput');
    const formImportar = document.querySelector('#btnImportar').closest('form');
    
    if (btnImportar && fileInput) {
        btnImportar.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                if (formImportar) {
                    formImportar.submit();
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
    
    if (costoInput && precioInput) {
        costoInput.addEventListener('input', calcularMargen);
        precioInput.addEventListener('input', calcularMargen);
    }
}

// ==================== CONFIGURAR PESO EN NUEVO PRODUCTO ====================

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

// ==================== CÓDIGO AUTOMÁTICO ====================

function configurarCodigoAutomatico() {
    const familiaSelect = document.getElementById('familia');
    const codigoInput = document.getElementById('codigo');
    
    if (familiaSelect && codigoInput) {
        const prefijos = {
            'EQUIPOS DE COMUNICACIÓN Y ELECTRÓNICA': 'ELE',
            'EQUIPOS DE PROTECCIÓN PERSONAL (EPP)': 'EPP',
            'EQUIPOS DE SOLDADURA': 'SOL',
            'HERRAMIENTAS ELÉCTRICAS': 'HEL',
            'HERRAMIENTAS MANUALES': 'HMA',
            'MATERIALES DE EMBALAJE': 'EMB',
            'MATERIALES DE LIMPIEZA Y MANTENIMIENTO': 'LIM',
            'MATERIALES DE SEGURIDAD Y SEÑALIZACIÓN': 'SEG',
            'MATERIALES ELÉCTRICOS': 'MEL',
            'MOBILIARIO Y EQUIPOS DE OFICINA': 'OFI',
            'PRODUCTOS QUÍMICOS Y ADHESIVOS': 'QUI',
            'REPUESTOS Y ACCESORIOS AUTOMOTRICES': 'AUT',
            'ROPA DE PROTECCIÓN': 'ROP'
        };
        
        familiaSelect.addEventListener('change', async () => {
            const familia = familiaSelect.value;
            const prefijo = prefijos[familia] || 'GEN';
            
            try {
                const response = await fetch(`/api/ultimo_codigo?prefijo=${prefijo}`);
                const data = await response.json();
                const numero = (data.ultimo_numero || 0) + 1;
                codigoInput.value = `${prefijo}-${numero.toString().padStart(4, '0')}`;
            } catch (error) {
                console.error("Error generando código:", error);
                codigoInput.value = `${prefijo}-0001`;
            }
        });
    }
}

// ==================== INICIALIZACIÓN PRINCIPAL ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log("🟢 Inicializando sistema de gestión de productos...");
    
    // Inicializar modales de Bootstrap
    const modalEditarElement = document.getElementById('modalEditarProducto');
    const modalEliminarElement = document.getElementById('modalEliminarProducto');
    
    if (modalEditarElement) {
        editModal = new bootstrap.Modal(modalEditarElement);
        console.log("✅ Modal de edición inicializado");
    } else {
        console.warn("⚠️ No se encontró el modal de edición");
    }
    
    if (modalEliminarElement) {
        deleteModal = new bootstrap.Modal(modalEliminarElement);
        console.log("✅ Modal de eliminación inicializado");
    } else {
        console.warn("⚠️ No se encontró el modal de eliminación");
    }
    
    // Cargar productos para selects
    cargarProductos();
    
    // Configurar event listeners para botones de editar y eliminar (delegación de eventos)
    document.body.addEventListener('click', (e) => {
        // Botón editar
        const btnEditar = e.target.closest('.btn-editar-producto');
        if (btnEditar) {
            e.preventDefault();
            const productoId = btnEditar.getAttribute('data-id');
            if (productoId) {
                abrirModalEdicion(productoId);
            } else {
                console.error("Botón de editar sin data-id");
                mostrarNotificacion("Error: Datos del producto no disponibles", "danger");
            }
            return;
        }
        
        // Botón eliminar
        const btnEliminar = e.target.closest('.btn-eliminar-producto');
        if (btnEliminar) {
            e.preventDefault();
            const productoId = btnEliminar.getAttribute('data-id');
            const descripcion = btnEliminar.getAttribute('data-descripcion');
            if (productoId) {
                abrirModalEliminacion(productoId, descripcion);
            } else {
                console.error("Botón de eliminar sin data-id");
                mostrarNotificacion("Error: Datos del producto no disponibles", "danger");
            }
            return;
        }
    });
    
    // Configurar eventos para el kárdex
    const modalKardex = document.getElementById('modalKardex');
    if (modalKardex) {
        modalKardex.addEventListener('shown.bs.modal', () => {
            const select = document.getElementById('kardex_producto_id');
            if (select && select.value) {
                cargarKardex(select.value);
            }
        });
    }
    
    const filtroKardex = document.getElementById('kardex_producto_id');
    if (filtroKardex) {
        filtroKardex.addEventListener('change', (e) => {
            cargarKardex(e.target.value);
        });
    }
    
    // Botón guardar movimiento kárdex
    const btnGuardarMovimiento = document.getElementById('btnGuardarMovimientoKardex');
    if (btnGuardarMovimiento) {
        const newBtn = btnGuardarMovimiento.cloneNode(true);
        btnGuardarMovimiento.parentNode.replaceChild(newBtn, btnGuardarMovimiento);
        newBtn.addEventListener('click', guardarMovimiento);
        console.log("✅ Botón guardar movimiento configurado");
    }
    
    // Botón guardar edición
    const btnGuardarEdicion = document.getElementById('btnGuardarEdicionProducto');
    if (btnGuardarEdicion) {
        const newBtn = btnGuardarEdicion.cloneNode(true);
        btnGuardarEdicion.parentNode.replaceChild(newBtn, btnGuardarEdicion);
        newBtn.addEventListener('click', guardarEdicion);
        console.log("✅ Botón guardar edición configurado");
    } else {
        console.warn("⚠️ No se encontró el botón guardar edición");
    }
    
    // Botón confirmar eliminación
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminarProducto');
    if (btnConfirmarEliminar) {
        const newBtn = btnConfirmarEliminar.cloneNode(true);
        btnConfirmarEliminar.parentNode.replaceChild(newBtn, btnConfirmarEliminar);
        newBtn.addEventListener('click', eliminarProducto);
        console.log("✅ Botón confirmar eliminación configurado");
    } else {
        console.warn("⚠️ No se encontró el botón confirmar eliminación");
    }
    
    // Configurar eventos para calcular margen en edición
    const editCosto = document.getElementById('edit_costo_unitario');
    const editPrecio = document.getElementById('edit_precio_unitario');
    
    if (editCosto && editPrecio) {
        editCosto.addEventListener('input', calcularMargenEdicion);
        editPrecio.addEventListener('input', calcularMargenEdicion);
    }
    
    // Configurar filtros
    const filtroFamilia = document.getElementById('filtro-familia');
    const filtroBusqueda = document.getElementById('filtro-busqueda');
    
    if (filtroFamilia) {
        filtroFamilia.addEventListener('change', aplicarFiltros);
    }
    
    if (filtroBusqueda) {
        filtroBusqueda.addEventListener('keyup', aplicarFiltros);
    }
    
    // Configurar otras funcionalidades
    configurarImportacion();
    configurarCalculoMargen();
    configurarPeso();
    configurarCodigoAutomatico();
    
    // Fecha por defecto para movimiento kárdex
    const fechaInput = document.getElementById('mov_kardex_fecha');
    if (fechaInput) {
        fechaInput.value = new Date().toISOString().split('T')[0];
    }
    
    console.log("✅ Inicialización completa");
});