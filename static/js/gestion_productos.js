// ==================== GESTIÓN DE PRODUCTOS - KCF CORPORACIÓN ====================
// Versión CORREGIDA - Compatible con jQuery y Fetch

// Variables globales
let editModal, deleteModal;

// ==================== NOTIFICACIONES ====================
function mostrarNotificacion(mensaje, tipo) {
    // Eliminar notificaciones anteriores
    $('.notificacion').remove();
    
    const color = tipo === 'success' ? '#198754' : (tipo === 'danger' ? '#dc3545' : '#0d6efd');
    const icono = tipo === 'success' ? 'check-circle' : (tipo === 'danger' ? 'exclamation-triangle' : 'info-circle');
    
    const notificacion = $(`
        <div class="alert text-white notificacion shadow-lg" style="background: ${color}; z-index: 10000;">
            <i class="bi bi-${icono} me-2"></i> ${mensaje}
        </div>
    `);
    
    $('body').append(notificacion);
    
    setTimeout(() => {
        notificacion.fadeOut(300, function() { $(this).remove(); });
    }, 3000);
}

// ==================== FILTROS Y BÚSQUEDA ====================
function filtrarTablaProductos() {
    let familia = $('#filtro-familia').val();
    let busqueda = $('#filtro-busqueda').val().toLowerCase();
    let visibleCount = 0;
    
    $('#tbody-productos tr').each(function() {
        let $row = $(this);
        let rowFamilia = $row.data('familia') || '';
        let textoBusqueda = ($row.data('descripcion') || '') + ' ' + ($row.data('codigo') || '');
        let matchFamilia = !familia || rowFamilia === familia;
        let matchBusqueda = !busqueda || textoBusqueda.toLowerCase().includes(busqueda);
        
        if (matchFamilia && matchBusqueda) {
            $row.show();
            visibleCount++;
        } else {
            $row.hide();
        }
    });
    
    $('#totalProductosCount').text(visibleCount);
}

function cargarSelectoresKardex() {
    let options = '<option value="">-- Seleccionar producto --</option>';
    $('#tbody-productos tr:visible').each(function() {
        let id = $(this).find('.btn-editar-producto').data('id');
        let desc = $(this).find('td:eq(3)').text().trim();
        let codigo = $(this).find('.badge.bg-secondary').text().trim();
        if (id) {
            options += `<option value="${id}">${codigo} - ${desc.substring(0, 50)}</option>`;
        }
    });
    $('#kardex_producto_id, #mov_kardex_producto_id').html(options);
}

// ==================== EDITAR PRODUCTO ====================
function calcularMargenEdicion() {
    const costo = parseFloat($('#edit_costo_unitario').val()) || 0;
    const precio = parseFloat($('#edit_precio_unitario').val()) || 0;
    
    if (costo > 0 && precio > 0) {
        const margen = ((precio - costo) / costo * 100).toFixed(2);
        $('#edit_margen').val(margen);
    } else {
        $('#edit_margen').val('');
    }
}

function guardarEdicion() {
    const id = $('#edit_id').val();
    
    if (!id) {
        mostrarNotificacion("Error: ID de producto no encontrado", "danger");
        return;
    }
    
    const datos = {
        familia: $('#edit_familia').val(),
        descripcion: $('#edit_descripcion').val(),
        descripcion_larga: $('#edit_descripcion_larga').val(),
        marca: $('#edit_marca').val(),
        modelo: $('#edit_modelo').val(),
        unidad: $('#edit_unidad').val(),
        volumen: $('#edit_volumen').val(),
        observaciones: $('#edit_observaciones').val(),
        transporte: $('#edit_transporte').val(),
        costo_unitario: parseFloat($('#edit_costo_unitario').val()) || 0,
        precio_unitario: parseFloat($('#edit_precio_unitario').val()) || 0,
        stock: parseInt($('#edit_stock').val()) || 0,
        peso: $('#edit_peso').val()
    };
    
    const btn = $('#btnGuardarEdicionProducto');
    const textoOriginal = btn.html();
    btn.prop('disabled', true);
    btn.html('<span class="spinner-border spinner-border-sm me-2"></span>Guardando...');
    
    $.ajax({
        url: '/api/productos/' + id,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(datos),
        success: function(response) {
            if (response.success) {
                mostrarNotificacion("✅ Producto actualizado correctamente", "success");
                if (editModal) editModal.hide();
                setTimeout(() => location.reload(), 1000);
            } else {
                mostrarNotificacion("❌ Error: " + (response.error || "No se pudo actualizar"), "danger");
            }
        },
        error: function(xhr) {
            console.error("Error al guardar edición:", xhr);
            let errorMsg = "Error de conexión al servidor";
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMsg = xhr.responseJSON.error;
            }
            mostrarNotificacion("❌ " + errorMsg, "danger");
        },
        complete: function() {
            btn.prop('disabled', false);
            btn.html(textoOriginal);
        }
    });
}

// ==================== ELIMINAR PRODUCTO ====================
function eliminarProducto() {
    const id = $('#eliminar_id_producto').val();
    
    if (!id) {
        mostrarNotificacion("Error: ID de producto no encontrado", "danger");
        return;
    }
    
    const btn = $('#confirmarEliminarProductoBtn');  // ← ID CORREGIDO
    const textoOriginal = btn.html();
    btn.prop('disabled', true);
    btn.html('<span class="spinner-border spinner-border-sm me-2"></span>Eliminando...');
    
    $.ajax({
        url: '/api/productos/' + id,
        method: 'DELETE',
        success: function(response) {
            if (response.success) {
                mostrarNotificacion("✅ Producto eliminado correctamente", "success");
                if (deleteModal) deleteModal.hide();
                setTimeout(() => location.reload(), 1000);
            } else {
                mostrarNotificacion("❌ Error: " + (response.error || "No se pudo eliminar"), "danger");
            }
        },
        error: function(xhr) {
            console.error("Error al eliminar producto:", xhr);
            mostrarNotificacion("❌ Error de conexión al servidor", "danger");
        },
        complete: function() {
            btn.prop('disabled', false);
            btn.html(textoOriginal);
        }
    });
}

// ==================== KÁRDEX ====================
function cargarKardex(productoId) {
    const tbody = $('#tbody-kardex');
    if (!productoId) {
        tbody.html('<tr><td colspan="8" class="text-center">Seleccione un producto</td></tr>');
        $('#kardex_stock_actual').text('0');
        $('#kardex_valor_total').text('S/ 0.00');
        return;
    }
    
    tbody.html('<tr><td colspan="8" class="text-center"><div class="spinner-border spinner-border-sm me-2"></div>Cargando...</td></tr>');
    
    $.ajax({
        url: '/api/movimientos_stock?producto_id=' + productoId,
        method: 'GET',
        success: function(movimientos) {
            if (!movimientos || movimientos.length === 0) {
                tbody.html('<tr><td colspan="8" class="text-center">No hay movimientos para este producto</td></tr>');
                actualizarStockProducto(productoId);
                return;
            }
            
            tbody.empty();
            let saldo = 0;
            
            movimientos.forEach(mov => {
                if (mov.tipo === 'ENTRADA') saldo += mov.cantidad;
                else if (mov.tipo === 'SALIDA') saldo -= mov.cantidad;
                else if (mov.tipo === 'AJUSTE') saldo = mov.cantidad;
                
                const fecha = mov.created_at ? new Date(mov.created_at).toLocaleDateString('es-PE') : '-';
                
                tbody.append(`
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
                `);
            });
            
            $('#kardex_stock_actual').text(saldo);
            actualizarValorTotal(productoId, saldo);
        },
        error: function(xhr) {
            console.error("Error al cargar kárdex:", xhr);
            tbody.html('<tr><td colspan="8" class="text-center text-danger">Error al cargar movimientos</td></tr>');
            mostrarNotificacion("Error al cargar kárdex", "danger");
        }
    });
}

function actualizarStockProducto(productoId) {
    $.ajax({
        url: '/api/productos/' + productoId,
        method: 'GET',
        success: function(p) {
            $('#kardex_stock_actual').text(p.stock || 0);
            actualizarValorTotal(productoId, p.stock || 0);
        }
    });
}

function actualizarValorTotal(productoId, stock) {
    $.ajax({
        url: '/api/productos/' + productoId,
        method: 'GET',
        success: function(p) {
            const valor = stock * (p.costo_unitario || 0);
            $('#kardex_valor_total').text(`S/ ${valor.toFixed(2)}`);
        }
    });
}

function guardarMovimiento() {
    const productoId = $('#mov_kardex_producto_id').val();
    const tipo = $('#mov_kardex_tipo').val();
    const cantidad = $('#mov_kardex_cantidad').val();
    const costo = $('#mov_kardex_costo').val();
    const referencia = $('#mov_kardex_referencia').val();
    const motivo = $('#mov_kardex_motivo').val();
    const fecha = $('#mov_kardex_fecha').val();
    
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
        motivo: motivo || null,
        fecha: fecha || new Date().toISOString().split('T')[0]
    };
    
    const btn = $('#btnGuardarMovimientoKardex');
    const textoOriginal = btn.html();
    btn.prop('disabled', true);
    btn.html('<span class="spinner-border spinner-border-sm me-2"></span>Guardando...');
    
    $.ajax({
        url: '/api/movimientos_stock',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(datos),
        success: function(response) {
            if (response.success) {
                mostrarNotificacion("✅ Movimiento registrado correctamente", "success");
                
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoMovimientoKardex'));
                if (modal) modal.hide();
                
                const select = $('#kardex_producto_id').val();
                if (select) {
                    cargarKardex(select);
                }
                
                $('#mov_kardex_cantidad').val('');
                $('#mov_kardex_costo').val('');
                $('#mov_kardex_referencia').val('');
                $('#mov_kardex_motivo').val('');
                
                setTimeout(() => location.reload(), 1500);
            } else {
                mostrarNotificacion("❌ " + (response.error || "Error al registrar movimiento"), "danger");
            }
        },
        error: function(xhr) {
            console.error("Error guardando movimiento:", xhr);
            mostrarNotificacion("❌ Error de conexión al servidor", "danger");
        },
        complete: function() {
            btn.prop('disabled', false);
            btn.html(textoOriginal);
        }
    });
}

// ==================== MARGEN EN NUEVO PRODUCTO ====================
function configurarCalculoMargen() {
    const costoInput = $('#costo_unitario');
    const precioInput = $('#precio_unitario');
    const margenInput = $('#margen_calculado_nuevo');
    
    function calcularMargen() {
        const costo = parseFloat(costoInput.val()) || 0;
        const precio = parseFloat(precioInput.val()) || 0;
        
        if (costo > 0 && precio > 0) {
            const margen = ((precio - costo) / costo * 100).toFixed(2);
            margenInput.val(margen + '%');
        } else {
            margenInput.val('');
        }
    }
    
    costoInput.on('input', calcularMargen);
    precioInput.on('input', calcularMargen);
}

// ==================== IMPORTAR EXCEL ====================
function configurarImportacion() {
    $('#btnImportarExcelTrigger').click(function() {
        $('#fileExcelInput').click();
    });
    
    $('#fileExcelInput').change(function() {
        if (this.files.length) {
            $('#importExcelForm').submit();
        }
    });
}

// ==================== INICIALIZACIÓN ====================
$(document).ready(function() {
    console.log("🟢 Inicializando sistema de gestión de productos...");
    
    // Inicializar modales
    const modalEditarElement = document.getElementById('modalEditarProducto');
    const modalEliminarElement = document.getElementById('modalEliminarProducto');
    
    if (modalEditarElement) {
        editModal = new bootstrap.Modal(modalEditarElement);
    }
    if (modalEliminarElement) {
        deleteModal = new bootstrap.Modal(modalEliminarElement);
    }
    
    // Filtros
    $('#filtro-familia, #filtro-busqueda').on('change keyup', function() {
        filtrarTablaProductos();
        cargarSelectoresKardex();
    });
    filtrarTablaProductos();
    cargarSelectoresKardex();
    
    // Sidebar Kárdex
    $('#sidebarKardexLink').click(function(e) {
        e.preventDefault();
        $('#modalKardex').modal('show');
        cargarSelectoresKardex();
    });
    
    // Botón guardar edición
    $('#btnGuardarEdicionProducto').click(guardarEdicion);
    
    // Botón confirmar eliminación
    $('#confirmarEliminarProductoBtn').click(eliminarProducto);
    
    // Botón guardar movimiento
    $('#btnGuardarMovimientoKardex').click(guardarMovimiento);
    
    // Calcular margen en edición
    $('#edit_costo_unitario, #edit_precio_unitario').on('input', calcularMargenEdicion);
    
    // Cargar kárdex al seleccionar producto
    $('#kardex_producto_id').change(function() {
        cargarKardex($(this).val());
    });
    
    // Configurar fecha por defecto en movimiento
    if ($('#mov_kardex_fecha').val() === '') {
        $('#mov_kardex_fecha').val(new Date().toISOString().split('T')[0]);
    }
    
    // Configurar importación
    configurarImportacion();
    configurarCalculoMargen();
    
    console.log("✅ Inicialización completa");
});