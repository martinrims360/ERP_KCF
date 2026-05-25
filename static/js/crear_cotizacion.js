// ==================== CREAR COTIZACIÓN JS COMPLETO ====================

document.addEventListener('DOMContentLoaded', () => {
    // ========================= HELPERS =========================
    const toNum = (v) => {
        const x = Number(String(v ?? '').replace(',', '.'));
        return Number.isFinite(x) ? x : 0;
    };

    let codigoCotizacionActual = '';
    let correlativoActual = 0;
    let usuarioActual = null;
    let esBorrador = true;
    let itemCounter = 0;

    // ========================= ASIGNAR ASESOR POR DEFECTO =========================
    function asignarAsesorPorDefecto() {
        console.log('📌 Asignando valores por defecto');
        const asesorInput = document.getElementById('asesor_comercial');
        const emailContacto = document.getElementById('email_contacto');
        const telefonoUser = document.getElementById('telefono_contacto_user');
        const usuarioIdInput = document.getElementById('usuario_id');
        const codigoVendedorSpan = document.getElementById('codigo_vendedor');
        
        if (asesorInput) asesorInput.value = 'Hellen Blas Principe';
        if (emailContacto) emailContacto.value = 'ventas@kcfcorporacion.com';
        if (telefonoUser) telefonoUser.value = '999932051';
        if (usuarioIdInput) usuarioIdInput.value = '1';
        if (codigoVendedorSpan) codigoVendedorSpan.textContent = 'HELLEN';
        
        usuarioActual = {
            id: 1,
            nombre_completo: 'Hellen Blas Principe',
            email: 'ventas@kcfcorporacion.com',
            telefono: '999932051',
            codigo_vendedor: 'HELLEN'
        };
    }

    async function obtenerUsuarioActual() {
        try {
            const response = await fetch('/api/usuarios/actual');
            const data = await response.json();
            if (data.success && data.data) {
                usuarioActual = data.data;
                const codigoVendedorSpan = document.getElementById('codigo_vendedor');
                if (codigoVendedorSpan && usuarioActual.codigo_vendedor) codigoVendedorSpan.textContent = usuarioActual.codigo_vendedor;
                const asesorInput = document.getElementById('asesor_comercial');
                if (asesorInput && usuarioActual.nombre_completo) {
                    asesorInput.value = usuarioActual.nombre_completo;
                    const usuarioIdInput = document.getElementById('usuario_id');
                    const emailContacto = document.getElementById('email_contacto');
                    const telefonoUser = document.getElementById('telefono_contacto_user');
                    if (usuarioIdInput) usuarioIdInput.value = usuarioActual.id;
                    if (emailContacto) emailContacto.value = usuarioActual.email || '';
                    if (telefonoUser) telefonoUser.value = usuarioActual.telefono || '';
                }
                return usuarioActual;
            }
            asignarAsesorPorDefecto();
            return usuarioActual;
        } catch (error) {
            console.error('Error obteniendo usuario:', error);
            asignarAsesorPorDefecto();
            return usuarioActual;
        }
    }

    function generarCodigoTemporal() {
        const fecha = new Date();
        const timestamp = `${fecha.getFullYear()}${String(fecha.getMonth() + 1).padStart(2, '0')}${String(fecha.getDate()).padStart(2, '0')}_${String(fecha.getHours()).padStart(2, '0')}${String(fecha.getMinutes()).padStart(2, '0')}${String(fecha.getSeconds()).padStart(2, '0')}`;
        const codigoVendedor = usuarioActual?.codigo_vendedor || 'HELLEN';
        return `TMP-${codigoVendedor}-${timestamp}`;
    }

    function actualizarNumeroCotizacionUI(codigo, esBorradorActual = esBorrador) {
        const numeroDiv = document.getElementById('numero_cotizacion');
        const tipoDocSpan = document.getElementById('tipo_documento');
        if (numeroDiv && codigo) {
            if (esBorradorActual) {
                numeroDiv.innerHTML = `<span style="font-size: 1rem; color: #f59e0b;">${codigo}</span><small style="display: block; font-size: 0.7rem; color: #f59e0b;">⚠️ BORRADOR</small>`;
                if (tipoDocSpan) tipoDocSpan.innerHTML = '<span class="badge-warning">BORRADOR</span>';
            } else {
                numeroDiv.innerHTML = `<span style="font-size: 1.2rem; color: #10b981;">${codigo}</span>`;
                if (tipoDocSpan) tipoDocSpan.innerHTML = '<span class="badge-success">OFICIAL</span>';
            }
            codigoCotizacionActual = codigo;
        }
        actualizarEstadoBotonPDF();
    }

    async function generarCodigoOficial() {
        if (!usuarioActual) await obtenerUsuarioActual();
        const fecha = new Date();
        const año = fecha.getFullYear();
        const mes = String(fecha.getMonth() + 1).padStart(2, '0');
        const dia = String(fecha.getDate()).padStart(2, '0');
        const codigoVendedor = usuarioActual?.codigo_vendedor || 'HELLEN';
        const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
        return `COT-${codigoVendedor}-${año}${mes}${dia}-${random}`;
    }

    async function inicializarCodigo() {
        await obtenerUsuarioActual();
        esBorrador = true;
        const codigoTemporal = generarCodigoTemporal();
        actualizarNumeroCotizacionUI(codigoTemporal, true);
        return codigoTemporal;
    }

    function actualizarEstadoBotonPDF() {
        const btnPdf = document.getElementById('btnPdf');
        const cotizacionId = document.getElementById('cotizacion_id')?.value;
        if (btnPdf) {
            if (cotizacionId && cotizacionId !== '' && cotizacionId !== 'None' && esBorrador === false) {
                btnPdf.disabled = false;
                btnPdf.classList.remove('opacity-50');
            } else {
                btnPdf.disabled = true;
                btnPdf.classList.add('opacity-50');
            }
        }
    }

    function mostrarNotificacion(mensaje, tipo) {
        const notificacion = document.createElement('div');
        notificacion.className = `alert alert-${tipo} position-fixed top-0 end-0 m-3`;
        notificacion.style.zIndex = '9999';
        notificacion.style.minWidth = '300px';
        notificacion.style.animation = 'slideIn 0.3s ease';
        notificacion.innerHTML = `<i class="bi bi-${tipo === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>${mensaje}`;
        document.body.appendChild(notificacion);
        setTimeout(() => notificacion.remove(), 3000);
    }

    // ========================= FUNCIÓN SUNAT =========================
    async function consultarSunat(ruc) {
        try {
            mostrarNotificacion(`🔍 Consultando RUC ${ruc} en SUNAT...`, 'info');
            const response = await fetch(`https://api.apis.net.pe/v2/sunat/ruc?numero=${ruc}`);
            if (!response.ok) throw new Error('Error al consultar SUNAT');
            const data = await response.json();
            if (data && data.razonSocial) {
                return {
                    success: true,
                    razon_social: data.razonSocial || '',
                    nombre_comercial: data.nombreComercial || '',
                    direccion: data.direccion || '',
                    estado: data.estado || ''
                };
            }
            return { success: false, error: 'No se encontraron datos para este RUC' };
        } catch (error) {
            console.error('Error consultando SUNAT:', error);
            return { success: false, error: error.message };
        }
    }

    async function autocompletarConSunat() {
        const tipoDocumento = document.getElementById('nuevo_tipo_documento')?.value;
        const numeroDocumento = document.getElementById('nuevo_numero_documento')?.value.trim();
        
        if (tipoDocumento !== 'RUC') {
            mostrarNotificacion('⚠️ La búsqueda en SUNAT solo está disponible para RUC', 'warning');
            return;
        }
        if (!numeroDocumento || numeroDocumento.length !== 11) {
            mostrarNotificacion('⚠️ Ingrese un RUC válido de 11 dígitos', 'warning');
            return;
        }
        
        const btnBuscar = document.getElementById('btnBuscarSunat');
        const textoOriginal = btnBuscar?.innerHTML;
        if (btnBuscar) {
            btnBuscar.innerHTML = '<i class="bi bi-hourglass-split"></i> Buscando...';
            btnBuscar.disabled = true;
        }
        
        try {
            const resultado = await consultarSunat(numeroDocumento);
            if (resultado.success) {
                document.getElementById('nuevo_razon_social').value = resultado.razon_social || '';
                document.getElementById('nuevo_nombre_comercial').value = resultado.nombre_comercial || '';
                document.getElementById('nuevo_direccion_fiscal').value = resultado.direccion || '';
                mostrarNotificacion('✅ Datos cargados desde SUNAT correctamente', 'success');
            } else {
                mostrarNotificacion('❌ ' + (resultado.error || 'No se encontraron datos para este RUC'), 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarNotificacion('❌ Error al consultar SUNAT', 'danger');
        } finally {
            if (btnBuscar) {
                btnBuscar.innerHTML = textoOriginal;
                btnBuscar.disabled = false;
            }
        }
    }

    // ========================= BOTÓN BUSCAR CLIENTE POR RUC =========================
    const btnBuscarClientePorRuc = document.getElementById('btnBuscarClientePorRuc');
    const buscarRucInput = document.getElementById('buscar_ruc');
    const btnLimpiarCliente = document.getElementById('btnLimpiarCliente');

    if (btnBuscarClientePorRuc) {
        btnBuscarClientePorRuc.addEventListener('click', async function(e) {
            e.preventDefault();
            const ruc = buscarRucInput?.value.trim();
            if (!ruc) { mostrarNotificacion('⚠️ Ingrese un RUC para buscar', 'warning'); return; }
            if (ruc.length !== 11) { mostrarNotificacion('⚠️ El RUC debe tener 11 dígitos', 'warning'); return; }
            
            const textoOriginal = btnBuscarClientePorRuc.innerHTML;
            btnBuscarClientePorRuc.innerHTML = '<i class="bi bi-hourglass-split"></i> Consultando...';
            btnBuscarClientePorRuc.disabled = true;
            
            try {
                const resultado = await consultarSunat(ruc);
                if (resultado.success) {
                    document.getElementById('cliente_razon_social').value = resultado.razon_social || '';
                    document.getElementById('cliente_doc').value = ruc;
                    document.getElementById('cliente_direccion').value = resultado.direccion || '';
                    mostrarNotificacion('✅ Datos cargados desde SUNAT correctamente', 'success');
                } else {
                    mostrarNotificacion('❌ ' + (resultado.error || 'No se encontraron datos para este RUC en SUNAT'), 'danger');
                }
            } catch (error) {
                mostrarNotificacion('❌ Error al consultar SUNAT: ' + error.message, 'danger');
            } finally {
                btnBuscarClientePorRuc.innerHTML = textoOriginal;
                btnBuscarClientePorRuc.disabled = false;
            }
        });
    }

    if (btnLimpiarCliente) {
        btnLimpiarCliente.addEventListener('click', function() {
            document.getElementById('cliente_id').value = '';
            document.getElementById('cliente_razon_social').value = '';
            document.getElementById('cliente_doc').value = '';
            document.getElementById('cliente_direccion').value = '';
            document.getElementById('telefono_contacto').value = '';
            if (buscarRucInput) buscarRucInput.value = '';
            mostrarNotificacion('🧹 Cliente limpiado', 'info');
        });
    }

    // ========================= OBTENER LISTA DE PRODUCTOS =========================
    function obtenerListaProductos() {
        const filas = document.querySelectorAll("#table-body tr");
        let listaProductos = [];
        filas.forEach(row => {
            const getInput = (selector) => { const el = row.querySelector(selector); return el ? el.value : 0; };
            const getText = (selector) => { const el = row.querySelector(selector); return el ? el.textContent : 0; };
            const producto = {
                producto_id: Number(getInput('.producto_id')) || null,
                cantidad: Number(getInput('.cantidad')),
                costo_unitario: Number(getInput('.precio_costo_unitario')),
                subtotal_costo: Number(getText('.subtotal_costo')),
                precio_venta_unitario: Number(getInput('.precio_venta_unitario_input')) || 0,
                subtotal_venta: Number(getText('.subtotal_venta_item')),
                descuento_porcentaje: Number(getInput('.descuento_porcentaje')) || 0,
                subtotal_venta_con_descuento: Number(getText('.subtotal_venta_desc'))
            };
            listaProductos.push(producto);
        });
        return listaProductos;
    }

    // ========================= BUSCAR CLIENTES =========================
    async function buscarClientes(q) {
        try {
            const res = await fetch(`/api/clientes/buscar?q=${encodeURIComponent(q)}`);
            const json = await res.json();
            return json.data || [];
        } catch (error) {
            console.error('Error buscando clientes:', error);
            return [];
        }
    }

    async function buscarProductos(q) {
        try {
            const res = await fetch(`/api/productos/buscar?q=${encodeURIComponent(q)}`);
            const json = await res.json();
            return json.data || [];
        } catch (error) {
            console.error('Error buscando productos:', error);
            return [];
        }
    }

    // ========================= GUARDAR COTIZACIÓN =========================
    async function guardarCotizacion() {
        const cliente_id = Number(document.getElementById('cliente_id')?.value || 0);
        if (!cliente_id) { mostrarNotificacion("⚠️ Selecciona cliente", "warning"); return; }
        const listaProductos = obtenerListaProductos();
        if (listaProductos.length === 0) { mostrarNotificacion("⚠️ Agrega items", "warning"); return; }
        
        const subtotal = Number(document.getElementById('summary_subtotal_venta_desc')?.textContent || 0);
        const igv = Number(document.getElementById('summary_igv')?.textContent || 0);
        const total = Number(document.getElementById('summary_total_venta')?.textContent || 0);
        
        const payload = {
            cliente_id: cliente_id,
            usuario_id: Number(document.getElementById("usuario_id")?.value || 0),
            estado: document.getElementById("estado")?.value || "En Proceso",
            subtotal: subtotal,
            igv: igv,
            total: total,
            forma_pago: document.getElementById("forma_pago")?.value || "",
            tiempo_entrega: document.getElementById("tiempo_entrega")?.value || "",
            almacen: document.getElementById("almacen")?.value || "",
            validez_oferta: document.getElementById("validez_oferta")?.value || "15 días",
            nota_cotizacion: document.getElementById('nota_cotizacion')?.value || "",
            notas: document.getElementById('notas')?.value || "",
            productos: listaProductos,
            codigo_cotizacion: codigoCotizacionActual,
            es_borrador: esBorrador
        };
        
        const btnGuardar = esBorrador ? document.getElementById('btnGuardarBorrador') : document.getElementById('btnGuardarOficial');
        const textoOriginal = btnGuardar?.innerHTML;
        if (btnGuardar) {
            btnGuardar.innerHTML = '<i class="bi bi-hourglass-split"></i> Guardando...';
            btnGuardar.disabled = true;
        }
        
        try {
            const res = await fetch('/api/cotizacion/guardar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (!json.success) {
                mostrarNotificacion("❌ Error: " + (json.error || "Error desconocido"), "danger");
                return;
            }
            document.getElementById('cotizacion_id').value = json.data.id;
            if (!esBorrador) actualizarEstadoBotonPDF();
            
            const modalBody = document.getElementById('modalConfirmacionBody');
            if (modalBody) {
                modalBody.innerHTML = `
                    <div class="text-center mb-3"><i class="bi bi-check-circle-fill" style="font-size: 48px; color: #10b981;"></i></div>
                    <div class="alert alert-success"><strong>✅ ¡Cotización guardada exitosamente!</strong></div>
                    <div><strong>Número:</strong> ${json.data.codigo_cotizacion}</div>
                    <div><strong>Tipo:</strong> ${esBorrador ? 'BORRADOR' : 'OFICIAL'}</div>
                `;
            }
            const modal = new bootstrap.Modal(document.getElementById('modalConfirmacion'));
            modal.show();
        } catch (err) {
            console.error(err);
            mostrarNotificacion("❌ Error de conexión con el servidor", "danger");
        } finally {
            if (btnGuardar) {
                btnGuardar.innerHTML = textoOriginal;
                btnGuardar.disabled = false;
            }
        }
    }

    async function convertirAOficial() {
        if (!esBorrador) {
            mostrarNotificacion("⚠️ Esta cotización ya es oficial", "warning");
            return;
        }
        const listaProductos = obtenerListaProductos();
        if (listaProductos.length === 0) {
            mostrarNotificacion("⚠️ Debe agregar al menos un producto antes de convertir a oficial", "warning");
            return;
        }
        if (!confirm("¿Convertir este borrador a cotización oficial?\n\nEsta acción generará un código único y definitivo.")) return;
        
        const nuevoCodigo = await generarCodigoOficial();
        if (nuevoCodigo) {
            esBorrador = false;
            actualizarNumeroCotizacionUI(nuevoCodigo, false);
            document.getElementById('estado').value = 'Generada';
            mostrarNotificacion(`✅ Cotización convertida a OFICIAL\nNúmero: ${nuevoCodigo}`, "success");
            await guardarCotizacion();
        } else {
            mostrarNotificacion("❌ Error al generar código oficial. Intente nuevamente.", "danger");
        }
    }

    function generatePdf() {
        const cotId = document.getElementById('cotizacion_id')?.value;
        if (!cotId || cotId === '' || cotId === 'None') {
            mostrarNotificacion("⚠️ Debe guardar la cotización primero", "warning");
            return;
        }
        if (esBorrador) {
            mostrarNotificacion("⚠️ Debe convertir la cotización a OFICIAL antes de generar PDF", "warning");
            return;
        }
        window.open(`/api/cotizacion/pdf/${cotId}`, '_blank');
    }

    // ========================= AGREGAR ITEM =========================
    function addItem() {
        itemCounter++;
        const row = document.createElement("tr");
        row.innerHTML = `
            <td class="col-item">${itemCounter}</td>
            <td class="col-codigo">
                <input type="text" class="codigo_producto" placeholder="Buscar producto..." style="width:100%;">
                <input type="hidden" class="producto_id">
            </td>
            <td class="col-desc"><input type="text" class="descripcion" readonly style="width:100%;"></td>
            <td class="col-marca"><input type="text" class="marca" readonly style="width:100%;"></td>
            <td class="col-modelo"><input type="text" class="modelo" readonly style="width:100%;"></td>
            <td class="col-cantidad"><input type="number" class="cantidad" value="1" step="1" style="width:100%;"></td>
            <td class="col-monto"><input type="number" class="precio_costo_unitario" value="0" step="0.01" style="width:100%;"></td>
            <td class="subtotal_costo">0.00</td>
            <td class="col-pv"><input type="number" class="precio_venta_unitario_input" value="0" step="0.01" style="width:100%;"></td>
            <td class="subtotal_venta_item">0.00</td>
            <td class="col-descuento"><input type="number" class="descuento_porcentaje" value="0" step="0.01" style="width:100%;"></td>
            <td class="subtotal_venta_desc">0.00</td>
            <td><button class="btn-del">🗑</button></td>
        `;
        
        const tableBody = document.getElementById('table-body');
        if (tableBody) tableBody.appendChild(row);
        
        // Autocomplete para producto
        const codigoInput = row.querySelector('.codigo_producto');
        if (codigoInput) {
            let timeoutId = null;
            codigoInput.addEventListener('input', async () => {
                const q = codigoInput.value.trim();
                if (timeoutId) clearTimeout(timeoutId);
                if (q.length < 2) { 
                    const portal = document.getElementById('portalSuggestions');
                    if (portal) portal.style.display = 'none';
                    return; 
                }
                timeoutId = setTimeout(async () => {
                    const productos = await buscarProductos(q);
                    const portal = document.getElementById('portalSuggestions');
                    if (!portal) return;
                    if (!productos.length) {
                        portal.innerHTML = '<div class="empty">❌ No se encontraron productos</div>';
                        portal.style.display = 'block';
                        const rect = codigoInput.getBoundingClientRect();
                        portal.style.left = rect.left + 'px';
                        portal.style.top = (rect.bottom + 4) + 'px';
                        return;
                    }
                    const html = productos.map(p => `<div class="item" data-id="${p.id}" data-codigo="${p.codigo}" data-descripcion="${p.descripcion}" data-marca="${p.marca || ''}" data-modelo="${p.modelo || ''}" data-costo="${p.ultimo_costo || 0}">
                        <strong>📦 ${p.codigo}</strong> - ${p.descripcion}<div class="meta">${p.marca || ''} • Costo: ${p.ultimo_costo || 0}</div></div>`).join('');
                    portal.innerHTML = html;
                    portal.style.display = 'block';
                    const rect = codigoInput.getBoundingClientRect();
                    portal.style.left = rect.left + 'px';
                    portal.style.top = (rect.bottom + 4) + 'px';
                    portal.style.minWidth = Math.max(rect.width, 280) + 'px';
                    
                    portal.querySelectorAll('.item').forEach(el => {
                        el.addEventListener('click', () => {
                            row.querySelector('.producto_id').value = el.dataset.id;
                            row.querySelector('.codigo_producto').value = el.dataset.codigo;
                            row.querySelector('.descripcion').value = el.dataset.descripcion;
                            row.querySelector('.marca').value = el.dataset.marca;
                            row.querySelector('.modelo').value = el.dataset.modelo;
                            row.querySelector('.precio_costo_unitario').value = el.dataset.costo;
                            portal.style.display = 'none';
                            recalculateAll();
                        });
                    });
                }, 300);
            });
        }
        
        const rec = () => { recalculateAll(); };
        row.querySelector('.cantidad')?.addEventListener('input', rec);
        row.querySelector('.precio_costo_unitario')?.addEventListener('input', rec);
        row.querySelector('.precio_venta_unitario_input')?.addEventListener('input', rec);
        row.querySelector('.descuento_porcentaje')?.addEventListener('input', rec);
        row.querySelector('.btn-del')?.addEventListener('click', () => { row.remove(); recalculateAll(); });
        
        recalculateAll();
    }

    function recalculateAll() {
        const rows = document.querySelectorAll("#table-body tr");
        let totalSubtotalVentaDesc = 0;

        rows.forEach(r => {
            const cantidad = Number(r.querySelector('.cantidad')?.value || 0);
            const costo = Number(r.querySelector('.precio_costo_unitario')?.value || 0);
            const subtotalCosto = cantidad * costo;
            const sc = r.querySelector('.subtotal_costo');
            if (sc) sc.textContent = subtotalCosto.toFixed(2);

            const pvUnit = Number(r.querySelector('.precio_venta_unitario_input')?.value || 0);
            const subtotalVenta = pvUnit * cantidad;
            const sv = r.querySelector('.subtotal_venta_item');
            if (sv) sv.textContent = subtotalVenta.toFixed(2);

            const descPct = Number(r.querySelector('.descuento_porcentaje')?.value || 0);
            const subtotalDesc = subtotalVenta * (1 - descPct / 100);
            const svd = r.querySelector('.subtotal_venta_desc');
            if (svd) svd.textContent = subtotalDesc.toFixed(2);
            totalSubtotalVentaDesc += subtotalDesc;
        });

        const igv = totalSubtotalVentaDesc * 0.18;
        const totalFinal = totalSubtotalVentaDesc + igv;

        document.getElementById('total_subtotal_venta_desc').textContent = totalSubtotalVentaDesc.toFixed(2);
        document.getElementById('summary_subtotal_venta_desc').textContent = totalSubtotalVentaDesc.toFixed(2);
        document.getElementById('summary_igv').textContent = igv.toFixed(2);
        document.getElementById('summary_total_venta').textContent = totalFinal.toFixed(2);
    }

    // ========================= AUTOCOMPLETE CLIENTE =========================
    const clienteRazonSocial = document.getElementById('cliente_razon_social');
    if (clienteRazonSocial) {
        let timeoutId = null;
        clienteRazonSocial.addEventListener('input', async () => {
            const q = clienteRazonSocial.value.trim();
            if (timeoutId) clearTimeout(timeoutId);
            if (q.length < 2) { 
                const portal = document.getElementById('portalSuggestions');
                if (portal) portal.style.display = 'none';
                return; 
            }
            timeoutId = setTimeout(async () => {
                const clientes = await buscarClientes(q);
                const portal = document.getElementById('portalSuggestions');
                if (!portal) return;
                if (!clientes.length) {
                    portal.innerHTML = '<div class="empty">No encontrado</div>';
                    portal.style.display = 'block';
                    const rect = clienteRazonSocial.getBoundingClientRect();
                    portal.style.left = rect.left + 'px';
                    portal.style.top = (rect.bottom + 4) + 'px';
                    return;
                }
                const html = clientes.map(c => `<div class="item" data-id="${c.id}" data-razon="${c.razon_social}" data-doc="${c.numero_documento || ''}" data-direccion="${c.direccion_fiscal || ''}" data-telefono="${c.telefono_contacto || ''}">
                    <strong>🏢 ${c.razon_social}</strong><div class="meta">${c.tipo_documento || 'DNI/RUC'} • ${c.numero_documento || 'Sin documento'}</div></div>`).join('');
                portal.innerHTML = html;
                portal.style.display = 'block';
                const rect = clienteRazonSocial.getBoundingClientRect();
                portal.style.left = rect.left + 'px';
                portal.style.top = (rect.bottom + 4) + 'px';
                portal.style.minWidth = Math.max(rect.width, 280) + 'px';
                
                portal.querySelectorAll('.item').forEach(el => {
                    el.addEventListener('click', () => {
                        document.getElementById('cliente_id').value = el.dataset.id;
                        document.getElementById('cliente_razon_social').value = el.dataset.razon;
                        document.getElementById('cliente_doc').value = el.dataset.doc || '';
                        document.getElementById('cliente_direccion').value = el.dataset.direccion || '';
                        document.getElementById('telefono_contacto').value = el.dataset.telefono || '';
                        portal.style.display = 'none';
                    });
                });
            }, 300);
        });
    }

    // ========================= GUARDAR NUEVO CLIENTE =========================
    async function guardarNuevoCliente() {
        const numeroDocumento = document.getElementById('nuevo_numero_documento')?.value.trim();
        const razonSocial = document.getElementById('nuevo_razon_social')?.value.trim();
        if (!numeroDocumento) { mostrarNotificacion('⚠️ Ingrese el número de documento', 'warning'); return; }
        if (!razonSocial) { mostrarNotificacion('⚠️ Ingrese la razón social', 'warning'); return; }
        
        const btnGuardar = document.getElementById('btnGuardarNuevoCliente');
        const textoOriginal = btnGuardar.innerHTML;
        btnGuardar.innerHTML = '<i class="bi bi-hourglass-split"></i> Guardando...';
        btnGuardar.disabled = true;
        
        try {
            const payload = {
                tipo_documento: document.getElementById('nuevo_tipo_documento')?.value,
                numero_documento: numeroDocumento,
                razon_social: razonSocial,
                nombre_comercial: document.getElementById('nuevo_nombre_comercial')?.value.trim() || '',
                direccion_fiscal: document.getElementById('nuevo_direccion_fiscal')?.value.trim() || '',
                telefono_contacto: document.getElementById('nuevo_telefono')?.value.trim() || '',
                email_contacto: document.getElementById('nuevo_email')?.value.trim() || '',
                nombre_contacto: document.getElementById('nuevo_nombre_contacto')?.value.trim() || ''
            };
            const response = await fetch('/api/clientes/crear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            if (result.success) {
                document.getElementById('formNuevoCliente')?.reset();
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoCliente'));
                modal.hide();
                mostrarNotificacion('✅ Cliente creado exitosamente', 'success');
                // Cargar el cliente recién creado
                if (result.data && result.data.id) {
                    document.getElementById('cliente_id').value = result.data.id;
                    document.getElementById('cliente_razon_social').value = razonSocial;
                    document.getElementById('cliente_doc').value = numeroDocumento;
                }
            } else {
                mostrarNotificacion('❌ Error: ' + (result.error || 'No se pudo crear el cliente'), 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarNotificacion('❌ Error de conexión', 'danger');
        } finally {
            btnGuardar.innerHTML = textoOriginal;
            btnGuardar.disabled = false;
        }
    }

    // ========================= EVENT LISTENERS =========================
    document.getElementById('btnGuardarBorrador')?.addEventListener('click', guardarCotizacion);
    document.getElementById('btnGuardarOficial')?.addEventListener('click', convertirAOficial);
    document.getElementById('btnPdf')?.addEventListener('click', generatePdf);
    document.getElementById('btnAgregarItem')?.addEventListener('click', addItem);
    document.getElementById('btnCrearCliente')?.addEventListener('click', () => {
        document.getElementById('formNuevoCliente')?.reset();
        new bootstrap.Modal(document.getElementById('modalNuevoCliente')).show();
    });
    document.getElementById('btnGuardarNuevoCliente')?.addEventListener('click', guardarNuevoCliente);
    document.getElementById('btnBuscarSunat')?.addEventListener('click', autocompletarConSunat);
    
    // Inicializar
    addItem();
    inicializarCodigo();
    
    // Si hay cotización ID en la URL, cargarla
    const cotId = new URLSearchParams(window.location.search).get('id');
    if (cotId) {
        document.getElementById('cotizacion_id').value = cotId;
        cargarCotizacion(cotId);
    }
    
    async function cargarCotizacion(id) {
        try {
            const res = await fetch(`/api/cotizacion/${id}`);
            const json = await res.json();
            if (!json.success) return;
            const data = json.data;
            document.getElementById('cliente_id').value = data.cliente_id || '';
            document.getElementById('cliente_razon_social').value = data.cliente || '';
            document.getElementById('cliente_doc').value = data.numero_documento || '';
            document.getElementById('cliente_direccion').value = data.direccion_fiscal || '';
            document.getElementById('estado').value = data.estado || 'En Proceso';
            document.getElementById('notas').value = data.notas || '';
            document.getElementById('forma_pago').value = data.forma_pago || '';
            document.getElementById('tiempo_entrega').value = data.tiempo_entrega || '';
            document.getElementById('almacen').value = data.almacen || '';
            document.getElementById('validez_oferta').value = data.validez_oferta || '';
            document.getElementById('nota_cotizacion').value = data.nota_cotizacion || '';
            
            // Limpiar tabla
            document.getElementById('table-body').innerHTML = '';
            itemCounter = 0;
            // Cargar productos
            if (data.detalle && data.detalle.length) {
                data.detalle.forEach(item => {
                    addItem();
                    const row = document.querySelector("#table-body tr:last-child");
                    if (row) {
                        row.querySelector('.producto_id').value = item.producto_id || '';
                        row.querySelector('.cantidad').value = item.cantidad || 0;
                        row.querySelector('.precio_costo_unitario').value = item.costo_unitario || 0;
                        row.querySelector('.precio_venta_unitario_input').value = item.precio_venta_unitario || 0;
                        row.querySelector('.descuento_porcentaje').value = Number(item.descuento_porcentaje || 0);
                        row.querySelector('.codigo_producto').value = item.codigo || '';
                        row.querySelector('.descripcion').value = item.descripcion || '';
                        row.querySelector('.marca').value = item.marca || '';
                        row.querySelector('.modelo').value = item.modelo || '';
                    }
                });
            }
            recalculateAll();
        } catch (err) {
            console.error(err);
        }
    }
});