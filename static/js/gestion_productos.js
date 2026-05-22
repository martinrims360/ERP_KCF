// ==================== KÁRDEX SIMPLE Y FUNCIONAL ====================

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

function mostrarNotificacion(mensaje, tipo) {
    const div = document.createElement('div');
    div.className = `alert alert-${tipo} notificacion`;
    div.innerHTML = `<i class="bi bi-${tipo === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>${mensaje}`;
    document.body.appendChild(div);
    setTimeout(() => {
        div.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => div.remove(), 300);
    }, 3000);
}

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log("🟢 Inicializando...");
    cargarProductos();
    
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
    
    const btnGuardar = document.getElementById('btnGuardarMovimientoKardex');
    if (btnGuardar) {
        btnGuardar.addEventListener('click', guardarMovimiento);
    }
    
    // Fecha por defecto
    const fechaInput = document.getElementById('mov_kardex_fecha');
    if (fechaInput) {
        fechaInput.value = new Date().toISOString().split('T')[0];
    }
    
    console.log("✅ Inicialización completa");
});