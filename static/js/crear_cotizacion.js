document.addEventListener('DOMContentLoaded', () => {

    // =========================
    // HELPERS
    // =========================
    const toNum = (v) => {
        const x = Number(String(v ?? '').replace(',', '.'));
        return Number.isFinite(x) ? x : 0;
    };

    // =========================
    // GENERACIÓN DE CÓDIGOS PERSONALIZADOS
    // =========================
    let codigoCotizacionActual = '';
    let correlativoActual = 0;
    let usuarioActual = null;
    let esBorrador = true;

    // Obtener usuario actual
    async function obtenerUsuarioActual() {
        try {
            const response = await fetch('/api/usuarios/actual');
            const data = await response.json();
            if (data.success && data.data) {
                usuarioActual = data.data;
                
                const codigoVendedorSpan = document.getElementById('codigo_vendedor');
                if (codigoVendedorSpan && usuarioActual.codigo_vendedor) {
                    codigoVendedorSpan.textContent = usuarioActual.codigo_vendedor;
                }
                
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
            return null;
        } catch (error) {
            console.error('Error obteniendo usuario:', error);
            return null;
        }
    }

    // Obtener último correlativo del usuario
    async function obtenerUltimoCorrelativo(usuarioId) {
        try {
            const response = await fetch(`/api/cotizacion/ultimo-correlativo?usuario_id=${usuarioId}`);
            const data = await response.json();
            if (data.success) {
                correlativoActual = data.correlativo || 0;
                return correlativoActual;
            }
            return 0;
        } catch (error) {
            console.error('Error obteniendo correlativo:', error);
            return 0;
        }
    }

    // Generar código temporal para borrador
    function generarCodigoTemporal() {
        const fecha = new Date();
        const timestamp = `${fecha.getFullYear()}${String(fecha.getMonth() + 1).padStart(2, '0')}${String(fecha.getDate()).padStart(2, '0')}_${String(fecha.getHours()).padStart(2, '0')}${String(fecha.getMinutes()).padStart(2, '0')}${String(fecha.getSeconds()).padStart(2, '0')}`;
        const codigoVendedor = usuarioActual?.codigo_vendedor || 'TMP';
        return `TMP-${codigoVendedor}-${timestamp}`;
    }

    // Actualizar número de cotización en UI
    function actualizarNumeroCotizacionUI(codigo, esBorradorActual = esBorrador) {
        const numeroDiv = document.getElementById('numero_cotizacion');
        const tipoDocSpan = document.getElementById('tipo_documento');
        
        if (numeroDiv && codigo) {
            if (esBorradorActual) {
                numeroDiv.innerHTML = `<span style="font-size: 1rem; color: #f59e0b;">${codigo}</span><small style="display: block; font-size: 0.7rem; color: #f59e0b;">⚠️ BORRADOR</small>`;
                if (tipoDocSpan) tipoDocSpan.innerHTML = '<span class="badge-warning">BORRADOR</span>';
            } else {
                numeroDiv.innerHTML = `<span style="font-size: 1.2rem; color: #10b981;">${codigo}</span><small style="display: block; font-size: 0.7rem; color: #6b7280;">Correlativo: ${correlativoActual}</small>`;
                if (tipoDocSpan) tipoDocSpan.innerHTML = '<span class="badge-success">OFICIAL</span>';
            }
            codigoCotizacionActual = codigo;
        }
    }

    // Generar código oficial
    async function generarCodigoOficial() {
        if (!usuarioActual) {
            await obtenerUsuarioActual();
        }
        
        if (usuarioActual) {
            await obtenerUltimoCorrelativo(usuarioActual.id);
            const nuevoCorrelativo = correlativoActual + 1;
            const codigoVendedor = usuarioActual.codigo_vendedor || `V${String(usuarioActual.id).padStart(3, '0')}`;
            const fecha = new Date();
            const año = fecha.getFullYear();
            const mes = String(fecha.getMonth() + 1).padStart(2, '0');
            const dia = String(fecha.getDate()).padStart(2, '0');
            
            const codigo = `COT-${codigoVendedor}-${año}${mes}${dia}-${String(nuevoCorrelativo).padStart(4, '0')}`;
            return codigo;
        }
        return null;
    }

    // Inicializar código (borrador temporal)
    async function inicializarCodigo() {
        await obtenerUsuarioActual();
        esBorrador = true;
        const codigoTemporal = generarCodigoTemporal();
        actualizarNumeroCotizacionUI(codigoTemporal, true);
        return codigoTemporal;
    }

    // =========================
    // NOTIFICACIONES
    // =========================
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

    // =========================
    // CONFIGURAR TIEMPO DE ENTREGA
    // =========================
    function configurarTiempoEntrega() {
        const select = document.getElementById('tiempo_entrega_select');
        const input = document.getElementById('tiempo_entrega');
        
        if (!select || !input) {
            console.warn('⚠️ Elementos de tiempo de entrega no encontrados');
            return;
        }
        
        console.log('✅ Configurando tiempo de entrega');
        
        select.addEventListener('change', function() {
            const valor = this.value;
            if (valor === 'personalizado') {
                input.style.display = 'block';
                input.value = '';
                input.placeholder = 'Ej: 10 días hábiles, 2 semanas, etc.';
                input.focus();
            } else if (valor === '') {
                input.style.display = 'none';
                input.value = '';
            } else {
                input.style.display = 'none';
                input.value = valor;
            }
        });
        
        input.addEventListener('focus', function() {
            select.value = 'personalizado';
            this.style.display = 'block';
        });
        
        if (input.value && input.value.trim() !== '') {
            let encontrado = false;
            for (let i = 0; i < select.options.length; i++) {
                if (select.options[i].value === input.value) {
                    select.value = input.value;
                    input.style.display = 'none';
                    encontrado = true;
                    break;
                }
            }
            if (!encontrado && input.value !== '') {
                select.value = 'personalizado';
                input.style.display = 'block';
            }
        }
    }

    // =========================
    // CARGAR PUNTOS DE ENTREGA
    // =========================
    async function cargarPuntosEntrega(clienteId) {
        const select = document.getElementById('punto_entrega');
        if (!select) return;

        select.innerHTML = `<option value="a_tratar">📝 A tratar (Negociación)</option>`;

        try {
            const res = await fetch(`/api/clientes/${clienteId}`);
            const json = await res.json();
            const puntos = json.data?.puntos_entrega || [];

            puntos.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.nombre_punto;
                opt.dataset.direccion = p.direccion || '';
                opt.dataset.telefono = p.telefono_contacto || '';
                opt.dataset.nombre_contacto = p.nombre_contacto || '';
                select.appendChild(opt);
            });
            
            select.onchange = function() {
                const opt = this.selectedOptions[0];
                const direccionEntrega = document.getElementById('direccion_entrega');
                const telefonoContacto = document.getElementById('telefono_contacto');
                const clienteContacto = document.getElementById('cliente_contacto');
                
                if (this.value === 'a_tratar') {
                    if (direccionEntrega) direccionEntrega.value = 'Por definir (Negociación)';
                    if (telefonoContacto) telefonoContacto.value = '';
                    if (clienteContacto) clienteContacto.value = 'A tratar';
                } else {
                    if (direccionEntrega) direccionEntrega.value = opt?.dataset?.direccion || '';
                    if (telefonoContacto) telefonoContacto.value = opt?.dataset?.telefono || '';
                    if (clienteContacto && opt?.dataset?.nombre_contacto) clienteContacto.value = opt.dataset.nombre_contacto;
                }
            };

        } catch (e) {
            console.error("Error cargando puntos", e);
        }
    }

    // =========================
    // CREAR NUEVO CLIENTE
    // =========================
    async function guardarNuevoCliente() {
        const tipoDocumento = document.getElementById('nuevo_tipo_documento')?.value;
        const numeroDocumento = document.getElementById('nuevo_numero_documento')?.value.trim();
        const razonSocial = document.getElementById('nuevo_razon_social')?.value.trim();
        
        if (!numeroDocumento) {
            mostrarNotificacion('⚠️ Ingrese el número de documento', 'warning');
            return;
        }
        
        if (!razonSocial) {
            mostrarNotificacion('⚠️ Ingrese la razón social', 'warning');
            return;
        }
        
        const btnGuardar = document.getElementById('btnGuardarNuevoCliente');
        const textoOriginal = btnGuardar.innerHTML;
        btnGuardar.innerHTML = '<i class="bi bi-hourglass-split"></i> Guardando...';
        btnGuardar.disabled = true;
        
        try {
            const payload = {
                tipo_documento: tipoDocumento,
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
                await cargarClienteEnCotizacion(result.data.id);
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

    async function cargarClienteEnCotizacion(clienteId) {
        try {
            const response = await fetch(`/api/clientes/${clienteId}`);
            const result = await response.json();
            
            if (result.success && result.data) {
                const cliente = result.data;
                
                document.getElementById('cliente_id').value = cliente.id;
                document.getElementById('cliente_razon_social').value = cliente.razon_social;
                document.getElementById('cliente_doc').value = cliente.numero_documento || '';
                document.getElementById('cliente_direccion').value = cliente.direccion_fiscal || '';
                document.getElementById('telefono_contacto').value = cliente.telefono_contacto || '';
                document.getElementById('cliente_contacto').value = cliente.nombre_contacto || '';
                
                await cargarPuntosEntrega(cliente.id);
                mostrarNotificacion('✅ Cliente cargado correctamente', 'success');
            }
        } catch (error) {
            console.error('Error cargando cliente:', error);
        }
    }

    // =========================
    // MODAL DE CONFIRMACIÓN
    // =========================
    function mostrarModalConfirmacion(datos) {
        const modalBody = document.getElementById('modalConfirmacionBody');
        if (!modalBody) return;
        
        const fecha = new Date();
        modalBody.innerHTML = `
            <div class="text-center mb-3"><i class="bi bi-check-circle-fill" style="font-size: 48px; color: #10b981;"></i></div>
            <div class="alert alert-success"><strong>✅ ¡Cotización guardada exitosamente!</strong></div>
            <div class="row"><div class="col-6"><strong>Número:</strong></div><div class="col-6">${datos.numero || datos.codigo_cotizacion}</div></div>
            <div class="row mt-2"><div class="col-6"><strong>Tipo:</strong></div><div class="col-6">${datos.tipo || (esBorrador ? 'BORRADOR' : 'OFICIAL')}</div></div>
            <div class="row mt-2"><div class="col-6"><strong>Asesor:</strong></div><div class="col-6">${usuarioActual?.nombre_completo || 'No asignado'}</div></div>
            <div class="row mt-2"><div class="col-6"><strong>Fecha:</strong></div><div class="col-6">${fecha.toLocaleDateString()}</div></div>
            <hr><div class="text-muted small"><i class="bi bi-info-circle"></i> El código es único y quedará registrado.</div>
        `;
        
        const modal = new bootstrap.Modal(document.getElementById('modalConfirmacion'));
        modal.show();
        
        document.getElementById('btnDescargarPDFModal').onclick = () => {
            const cotId = document.getElementById('cotizacion_id')?.value;
            if (cotId) window.open(`/api/cotizacion/pdf/${cotId}`, '_blank');
            else alert('⚠️ Guarde primero la cotización');
        };
        
        document.getElementById('btnNuevaCotizacionModal').onclick = () => {
            window.location.href = '/cotizacion/nueva';
        };
    }

    // =========================
    // ESTADO GLOBAL
    // =========================
    let estadoCotizacion = 'En Proceso';
    let cotizacionBloqueada = false;
    let datosModificados = false;
    let itemCounter = 0;
    let modoConsulta = false;

    const tableBody = document.getElementById('table-body');
    const portal = document.getElementById('portalSuggestions');

    function portalHide() {
        if (portal) {
            portal.style.display = 'none';
            portal.innerHTML = '';
        }
    }

    function portalShow(inputEl, html) {
        if (!portal) return;
        const rect = inputEl.getBoundingClientRect();
        portal.style.left = rect.left + 'px';
        portal.style.top = (rect.bottom + 4) + 'px';
        portal.style.minWidth = Math.max(rect.width, 280) + 'px';
        portal.innerHTML = html;
        portal.style.display = 'block';
    }

    // =========================
    // OBTENER LISTA DE PRODUCTOS
    // =========================
    function obtenerListaProductos() {
        const filas = document.querySelectorAll("#table-body tr");
        let listaProductos = [];

        filas.forEach(row => {
            const getInput = (selector) => {
                const el = row.querySelector(selector);
                return el ? el.value : 0;
            };

            const getText = (selector) => {
                const el = row.querySelector(selector);
                return el ? el.textContent : 0;
            };

            const producto = {
                producto_id: Number(getInput('.producto_id')) || null,
                cantidad: Number(getInput('.cantidad')),
                costo_unitario: Number(getInput('.precio_costo_unitario')),
                subtotal_costo: Number(getText('.subtotal_costo')),
                margen_porcentaje: Number(getInput('.margen_venta')),
                precio_venta_unitario: Number(getInput('.precio_venta_unitario_input')),
                subtotal_venta: Number(getText('.subtotal_venta_item')),
                descuento_porcentaje: Number(getInput('.descuento_porcentaje')),
                precio_venta_con_descuento: Number(getText('.precio_unitario_venta_desc')),
                subtotal_venta_con_descuento: Number(getText('.subtotal_venta_desc')),
                descuento_total: Number(getText('.descuento_subtotal')),
                margen_final: Number(getText('.margen_final'))
            };

            listaProductos.push(producto);
        });

        return listaProductos;
    }

    // =========================
    // FUNCIONES DE BÚSQUEDA
    // =========================
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

    async function buscarAsesores(q) {
        try {
            const res = await fetch(`/api/usuarios/buscar?q=${encodeURIComponent(q)}`);
            const json = await res.json();
            if (!json.success) return [];
            return json.data || [];
        } catch (error) {
            console.error('Error buscando asesores:', error);
            return [];
        }
    }

    async function buscarContactos(clienteId, q) {
        if (!clienteId) return [];
        try {
            const res = await fetch(`/api/clientes/${clienteId}/contactos?q=${encodeURIComponent(q)}`);
            const json = await res.json();
            return json.data || [];
        } catch (error) {
            console.error('Error buscando contactos:', error);
            return [];
        }
    }

    // =========================
    // GUARDAR COTIZACIÓN
    // =========================
    async function guardarCotizacion() {
        const cliente_id = Number(document.getElementById('cliente_id')?.value || 0);
        if (!cliente_id) { mostrarNotificacion("⚠️ Selecciona cliente", "warning"); return; }

        const listaProductos = obtenerListaProductos();
        if (listaProductos.length === 0) { mostrarNotificacion("⚠️ Agrega items", "warning"); return; }
        
        for (let i = 0; i < listaProductos.length; i++) {
            if (!listaProductos[i].producto_id) { mostrarNotificacion(`⚠️ Falta seleccionar producto en la fila ${i + 1}`, "warning"); return; }
        }
        
        const subtotal = Number(document.getElementById('summary_subtotal_venta_desc')?.textContent || 0);
        const igv = Number(document.getElementById('summary_igv')?.textContent || 0);
        const total = Number(document.getElementById('summary_total_venta')?.textContent || 0);
        
        const payload = {
            cliente_id: cliente_id,
            usuario_id: Number(document.getElementById("usuario_id")?.value || 0),
            estado: document.getElementById("estado")?.value || "En Proceso",
            subtotal: subtotal, igv: igv, total: total,
            forma_pago: document.getElementById("forma_pago")?.value || "",
            tiempo_entrega: document.getElementById("tiempo_entrega")?.value || "",
            almacen: document.getElementById("almacen")?.value || "",
            validez_oferta: document.getElementById("validez_oferta")?.value || "",
            notas: document.getElementById('notas')?.value || "",
            productos: listaProductos,
            codigo_cotizacion: codigoCotizacionActual,
            correlativo: esBorrador ? 0 : correlativoActual + 1,
            es_borrador: esBorrador
        };

        try {
            const res = await fetch('/api/cotizacion/guardar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (!json.success) { mostrarNotificacion("❌ Error: " + json.error, "danger"); return; }
            
            document.getElementById('cotizacion_id').value = json.data.id;
            if (!esBorrador) correlativoActual++;
            mostrarModalConfirmacion({ id: json.data.id, numero: json.data.codigo_cotizacion, tipo: esBorrador ? 'BORRADOR' : 'OFICIAL' });
        } catch (err) { console.error(err); mostrarNotificacion("❌ Error servidor", "danger"); }
    }

    // =========================
    // CONVERTIR A OFICIAL
    // =========================
    async function convertirAOficial() {
        if (!esBorrador) { mostrarNotificacion("⚠️ Esta cotización ya es oficial", "warning"); return; }
        if (!confirm("¿Convertir este borrador a cotización oficial?")) return;
        
        const nuevoCodigo = await generarCodigoOficial();
        if (nuevoCodigo) {
            esBorrador = false;
            actualizarNumeroCotizacionUI(nuevoCodigo, false);
            document.getElementById('estado').value = 'Generada';
            mostrarNotificacion(`✅ Cotización convertida a OFICIAL\nNúmero: ${nuevoCodigo}`, "success");
            await guardarCotizacion();
        }
    }

    // =========================
    // SET PRODUCTO EN FILA
    // =========================
    function setProductoEnFila(row, p) {  
        row.querySelector('.producto_id').value = p.id;
        row.querySelector('.codigo_producto').value = p.codigo || "";
        row.querySelector('.descripcion').value = p.descripcion || "";
        row.querySelector('.marca').value = p.marca || "";
        row.querySelector('.modelo').value = p.modelo || "";
    }

    // =========================
    // AUTOCOMPLETES
    // =========================
    function attachClienteAutocomplete(idInput) {
        const input = document.getElementById(idInput);
        if (!input) return;
        let timeoutId = null;

        input.addEventListener('input', async () => {
            const q = input.value.trim();
            if (timeoutId) clearTimeout(timeoutId);
            if (q.length < 2) { portalHide(); return; }
            
            timeoutId = setTimeout(async () => {
                const clientes = await buscarClientes(q);
                if (!clientes.length) { portalShow(input, `<div class="empty">No encontrado</div>`); return; }

                const html = clientes.map(c => `<div class="item" data-id="${c.id}" data-razon="${c.razon_social}" data-doc="${c.numero_documento || ''}" data-direccion="${c.direccion_fiscal || ''}" data-telefono="${c.telefono_contacto || ''}" data-contacto="${c.nombre_contacto || ''}">
                    <strong>🏢 ${c.razon_social}</strong><div class="meta">${c.tipo_documento || 'DNI/RUC'} • ${c.numero_documento || 'Sin documento'}</div></div>`).join('');
                portalShow(input, html);

                portal.querySelectorAll('.item').forEach(el => {
                    el.addEventListener('click', async () => {
                        document.getElementById('cliente_id').value = el.dataset.id;
                        document.getElementById('cliente_razon_social').value = el.dataset.razon;
                        document.getElementById('cliente_doc').value = el.dataset.doc || '';
                        document.getElementById('cliente_direccion').value = el.dataset.direccion || '';
                        document.getElementById('telefono_contacto').value = el.dataset.telefono || '';
                        document.getElementById('cliente_contacto').value = el.dataset.contacto || '';
                        await cargarPuntosEntrega(el.dataset.id);
                        portalHide();
                    });
                });
            }, 300);
        });
    }

    function attachProductoAutocomplete(row) {
        const input = row.querySelector('.codigo_producto');
        if (!input) return;
        let timeoutId = null;

        input.addEventListener('input', async () => {
            const q = input.value.trim();
            if (timeoutId) clearTimeout(timeoutId);
            if (q.length < 2) { portalHide(); return; }
            
            timeoutId = setTimeout(async () => {
                const productos = await buscarProductos(q);
                if (!productos.length) { portalShow(input, `<div class="empty">No encontrado</div>`); return; }

                const html = productos.map(p => `<div class="item" data-id="${p.id}" data-codigo="${p.codigo}" data-descripcion="${p.descripcion}" data-marca="${p.marca || ''}" data-modelo="${p.modelo || ''}">
                    <strong>📦 ${p.codigo}</strong> - ${p.descripcion}<div class="meta">${p.marca || ''} • ${p.unidad || ''}</div></div>`).join('');
                portalShow(input, html);

                portal.querySelectorAll('.item').forEach(el => {
                    el.addEventListener('click', () => {
                        setProductoEnFila(row, { id: el.dataset.id, codigo: el.dataset.codigo, descripcion: el.dataset.descripcion, marca: el.dataset.marca, modelo: el.dataset.modelo });
                        portalHide();
                        recalculateAll();
                    });
                });
            }, 300);
        });
    }

    function attachAsesorAutocomplete() {
        const input = document.getElementById('asesor_comercial');
        if (!input) return;
        let timeoutId = null;

        input.addEventListener('input', async () => {
            const q = input.value.trim();
            if (timeoutId) clearTimeout(timeoutId);
            if (q.length < 2) { portalHide(); return; }
            
            timeoutId = setTimeout(async () => {
                const asesores = await buscarAsesores(q);
                if (!asesores.length) { portalShow(input, `<div class="empty">Asesor no encontrado</div>`); return; }

                const html = asesores.map(a => `<div class="item" data-id="${a.id}" data-nombre="${a.nombre_completo}" data-email="${a.email || ''}" data-telefono="${a.telefono || ''}">
                    <strong>👨‍💼 ${a.nombre_completo}</strong><div class="meta">${a.rol || 'Asesor'} • ${a.codigo_vendedor || ''}</div></div>`).join('');
                portalShow(input, html);

                portal.querySelectorAll('.item').forEach(el => {
                    el.addEventListener('click', () => {
                        document.getElementById("usuario_id").value = el.dataset.id;
                        document.getElementById('asesor_comercial').value = el.dataset.nombre;
                        document.getElementById('email_contacto').value = el.dataset.email;
                        document.getElementById('telefono_contacto_user').value = el.dataset.telefono;
                        portalHide();
                    });
                });
            }, 300);
        });
    }

    function attachContactoAutocomplete() {
        const input = document.getElementById('cliente_contacto');
        if (!input) return;
        let timeoutId = null;
        
        input.addEventListener('input', async () => {
            const q = input.value.trim();
            const clienteId = document.getElementById('cliente_id')?.value;
            if (timeoutId) clearTimeout(timeoutId);
            
            if (!clienteId) {
                portalShow(input, `<div class="item" data-value="A tratar"><strong>📝 A tratar</strong><div class="meta">Contacto por definir</div></div>`);
                return;
            }
            
            timeoutId = setTimeout(async () => {
                const contactos = await buscarContactos(clienteId, q);
                let html = '';
                if (contactos.length > 0) {
                    html = contactos.map(c => `<div class="item" data-value="${c.nombre_contacto}"><strong>👤 ${c.nombre_contacto}</strong><div class="meta">${c.cargo || 'Contacto'} • ${c.telefono || ''}</div></div>`).join('');
                }
                html += `<div class="item" data-value="A tratar"><strong>📝 A tratar</strong><div class="meta">Negociación</div></div>`;
                portalShow(input, html);
                
                portal.querySelectorAll('.item').forEach(el => {
                    el.addEventListener('click', () => { input.value = el.dataset.value; portalHide(); });
                });
            }, 300);
        });
    }

    // =========================
    // RECALCULAR
    // =========================
    function recalculateAll() {
        const rows = document.querySelectorAll("#table-body tr");
        const montoTransporte = Number(document.getElementById('monto_transporte')?.value || 0);
        let totalSubtotalCosto = 0;

        rows.forEach(r => {
            const cantidad = Number(r.querySelector('.cantidad')?.value || 0);
            const costo = Number(r.querySelector('.precio_costo_unitario')?.value || 0);
            const subtotal = cantidad * costo;
            const sc = r.querySelector('.subtotal_costo');
            if (sc) sc.textContent = subtotal.toFixed(2);
            totalSubtotalCosto += subtotal;
        });
       
        rows.forEach(r => {
            const cantidad = Number(r.querySelector('.cantidad')?.value || 0);
            const subtotalCosto = Number(r.querySelector('.subtotal_costo')?.textContent || 0);
            const prorrateo = totalSubtotalCosto > 0 ? (montoTransporte * (subtotalCosto / totalSubtotalCosto)) : 0;
            const totalCosto = subtotalCosto + prorrateo;
            const precioUnitario = cantidad > 0 ? totalCosto / cantidad : 0;

            const set = (cls, val) => { const el = r.querySelector(cls); if (el) el.textContent = val.toFixed(2); };
            set('.transporte_prorrateo', prorrateo);
            set('.total_costo', totalCosto);
            set('.precio_unitario_costo_total', precioUnitario);

            const margen = Number(r.querySelector('.margen_venta')?.value || 0);
            const pvManual = Number(r.querySelector('.precio_venta_unitario_input')?.value || 0);
            const pvUnit = pvManual > 0 ? pvManual : precioUnitario * (1 + margen / 100);
            const subtotalVenta = pvUnit * cantidad;
            const descPct = Number(r.querySelector('.descuento_porcentaje')?.value || 0);
            const pvDesc = pvUnit * (1 - descPct / 100);
            const subtotalDesc = pvDesc * cantidad;
            
            set('.precio_venta_unitario_calc', pvUnit);
            set('.subtotal_venta_item', subtotalVenta);
            set('.precio_unitario_venta_desc', pvDesc);
            set('.subtotal_venta_desc', subtotalDesc);
        });

        let totalVentaDesc = 0;
        rows.forEach(r => { totalVentaDesc += Number(r.querySelector('.subtotal_venta_desc')?.textContent || 0); });
        const igv = totalVentaDesc * 0.18;
        const totalFinal = totalVentaDesc + igv;

        document.getElementById('summary_subtotal_venta_desc').textContent = totalVentaDesc.toFixed(2);
        document.getElementById('summary_igv').textContent = igv.toFixed(2);
        document.getElementById('summary_total_venta').textContent = totalFinal.toFixed(2);
    }

    // =========================
    // AGREGAR ITEMS
    // =========================
    function addItem() {
        if (cotizacionBloqueada) { mostrarNotificacion("⚠️ La cotización está bloqueada.", "warning"); return; }
        itemCounter++;
        const row = document.createElement("tr");
        row.innerHTML = `<td class="col-item">${itemCounter}</td>
            <td class="col-codigo"><input type="text" class="codigo_producto" placeholder="Código"><input type="hidden" class="producto_id"></td>
            <td class="col-desc"><input type="text" class="descripcion"></td>
            <td class="col-marca"><input type="text" class="marca"></td>
            <td class="col-modelo"><input type="text" class="modelo"></td>
            <td class="col-cantidad"><input type="number" class="cantidad" value="1" step="0.01"></td>
            <td class="col-monto"><input type="number" class="precio_costo_unitario" value="0" step="0.01"></td>
            <td class="subtotal_costo">0.00</td><td class="transporte_prorrateo">0.00</td><td class="total_costo">0.00</td>
            <td class="precio_unitario_costo_total">0.00</td>
            <td><input type="number" class="margen_venta" value="20" step="0.01"></td>
            <td><input type="number" class="precio_venta_unitario_input" value="0" step="0.01"></td>
            <td class="precio_venta_unitario_calc">0.00</td><td class="subtotal_venta_item">0.00</td>
            <td><input type="number" class="descuento_porcentaje" value="0" step="0.01"></td>
            <td class="precio_unitario_venta_desc">0.00</td><td class="subtotal_venta_desc">0.00</td>
            <td><button class="btn-del">🗑</button></td>`;
        if (tableBody) tableBody.appendChild(row);
        attachProductoAutocomplete(row);
        
        const rec = () => { if (!modoConsulta) { recalculateAll(); datosModificados = true; } };
        row.querySelector('.cantidad')?.addEventListener('input', rec);
        row.querySelector('.precio_costo_unitario')?.addEventListener('input', rec);
        row.querySelector('.margen_venta')?.addEventListener('input', rec);
        row.querySelector('.precio_venta_unitario_input')?.addEventListener('input', rec);
        row.querySelector('.descuento_porcentaje')?.addEventListener('input', rec);
        row.querySelector('.btn-del')?.addEventListener('click', () => { row.remove(); recalculateAll(); });
        setTimeout(recalculateAll, 50);
    }

    // =========================
    // ESTADO VISUAL
    // =========================
    function actualizarEstadoVisual() {
        const estadoElement = document.getElementById('estado_fixed');
        const estadoTexto = document.getElementById('estado_texto');
        if (!estadoElement || !estadoTexto) return;
        estadoTexto.textContent = estadoCotizacion.toUpperCase();
        estadoElement.className = 'erp-status ';
        if (estadoCotizacion === 'En Proceso') estadoElement.classList.add('estado-en-proceso');
        else if (estadoCotizacion === 'Generada') estadoElement.classList.add('estado-generada');
        else if (estadoCotizacion === 'Aceptada por Cliente') estadoElement.classList.add('estado-aceptada');
        else if (estadoCotizacion === 'Rechazada') estadoElement.classList.add('estado-rechazada');
        else estadoElement.classList.add('estado-en-proceso');
        actualizarBotones();
    }

    function actualizarBotones() {
        const pdfBtn = document.getElementById('btnPdf');
        const guardarBorrador = document.getElementById('btnGuardarBorrador');
        const guardarOficial = document.getElementById('btnGuardarOficial');
        const agregarBtn = document.getElementById('btnAgregarItem');
        if (modoConsulta) {
            if (guardarBorrador) guardarBorrador.disabled = true;
            if (guardarOficial) guardarOficial.disabled = true;
            if (agregarBtn) agregarBtn.disabled = true;
            if (pdfBtn) pdfBtn.disabled = false;
            cotizacionBloqueada = true;
            return;
        }
        if (estadoCotizacion === 'En Proceso') {
            cotizacionBloqueada = false;
            if (guardarBorrador) guardarBorrador.disabled = false;
            if (guardarOficial) guardarOficial.disabled = false;
        } else {
            cotizacionBloqueada = true;
            if (guardarBorrador) guardarBorrador.disabled = true;
            if (guardarOficial) guardarOficial.disabled = true;
        }
    }

    function aplicarBloqueoUI() {
        const disabled = cotizacionBloqueada;
        document.querySelectorAll('#table-body input').forEach(i => i.disabled = disabled);
        ['cliente_razon_social', 'cliente_doc', 'cliente_telefono', 'cliente_contacto', 'numero_requerimiento', 'direccion_entrega', 'punto_entrega', 'estado'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.disabled = disabled;
        });
        ['asesor_comercial', 'email_contacto', 'telefono_contacto', 'forma_pago', 'tiempo_entrega', 'validez_oferta', 'descuento_porcentaje', 'nota_cotizacion', 'notas', 'monto_transporte'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.disabled = disabled;
        });
        const btnAgregar = document.getElementById('btnAgregarItem');
        if (btnAgregar) btnAgregar.disabled = disabled;
        document.querySelectorAll('#table-body .btn-del').forEach(b => b.disabled = disabled);
    }

    function generatePdf() {
        const cotId = document.getElementById('cotizacion_id')?.value;
        if (!cotId) { mostrarNotificacion("⚠️ Guarda primero la cotización", "warning"); return; }
        window.open(`/api/cotizacion/pdf/${cotId}`, '_blank');
    }

    function showModificarModal() {
        const modal = document.getElementById('modalModificar');
        if (modal) modal.style.display = 'block';
    }

    function showAceptadaModal() {
        if (estadoCotizacion !== 'Generada' && estadoCotizacion !== 'oficial') {
            mostrarNotificacion("⚠️ Solo cotizaciones oficiales pueden ser aceptadas", "warning");
            return;
        }
        const modal = document.getElementById('modalAceptada');
        if (modal) modal.style.display = 'block';
    }

    async function cargarCotizacion(id) {
        try {
            const res = await fetch(`/api/cotizacion/${id}`);
            const json = await res.json();
            if (!json.success) { mostrarNotificacion("Error al cargar cotización", "danger"); return; }
            const data = json.data;
            if (data.codigo_cotizacion) {
                codigoCotizacionActual = data.codigo_cotizacion;
                correlativoActual = data.correlativo || 0;
                esBorrador = data.codigo_cotizacion.startsWith('TMP-');
                actualizarNumeroCotizacionUI(data.codigo_cotizacion, esBorrador);
            }
            await cargarPuntosEntrega(data.cliente_id);
            document.getElementById('cliente_id').value = data.cliente_id || '';
            document.getElementById('cliente_razon_social').value = data.cliente || '';
            document.getElementById('estado').value = data.estado || '';
            document.getElementById('notas').value = data.notas || '';
            document.getElementById('cliente_doc').value = data.numero_documento || '';
            document.getElementById('cliente_direccion').value = data.direccion_fiscal || '';
            document.getElementById('cliente_contacto').value = data.nombre_contacto || '';
            document.getElementById('usuario_id').value = data.usuario_id || '';
            document.getElementById('asesor_comercial').value = data.nombre_completo || '';
            document.getElementById('email_contacto').value = data.email || '';
            document.getElementById('telefono_contacto_user').value = data.telefono || '';
            document.getElementById('forma_pago').value = data.forma_pago || '';
            document.getElementById('tiempo_entrega').value = data.tiempo_entrega || '';
            document.getElementById('almacen').value = data.almacen || '';
            document.getElementById('validez_oferta').value = data.validez_oferta || '';
            document.getElementById('summary_subtotal_venta_desc').textContent = Number(data.subtotal || 0).toFixed(2);
            document.getElementById('summary_igv').textContent = Number(data.igv || 0).toFixed(2);
            document.getElementById('summary_total_venta').textContent = Number(data.total || 0).toFixed(2);
            document.getElementById('table-body').innerHTML = '';
            itemCounter = 0;
            (data.detalle || []).forEach(item => {
                addItem();
                const row = document.querySelector("#table-body tr:last-child");
                if (row) {
                    row.querySelector('.producto_id').value = item.producto_id || '';
                    row.querySelector('.cantidad').value = item.cantidad || 0;
                    row.querySelector('.precio_costo_unitario').value = item.costo_unitario || 0;
                    row.querySelector('.margen_venta').value = item.margen_porcentaje || 0;
                    row.querySelector('.precio_venta_unitario_input').value = item.precio_venta_unitario || 0;
                    row.querySelector('.descuento_porcentaje').value = Number(item.descuento_porcentaje || 0);
                    row.querySelector('.codigo_producto').value = item.codigo || '';
                    row.querySelector('.descripcion').value = item.descripcion || '';
                    row.querySelector('.marca').value = item.marca || '';
                    row.querySelector('.modelo').value = item.modelo || '';
                }
            });
            recalculateAll();
            configurarTiempoEntrega();
        } catch (err) { console.error(err); mostrarNotificacion("Error cargando cotización", "danger"); }
    }

    // =========================
    // EVENTOS
    // =========================
    document.getElementById('btnGuardar')?.addEventListener('click', guardarCotizacion);
    document.getElementById('btnGuardarBorrador')?.addEventListener('click', guardarCotizacion);
    document.getElementById('btnGuardarOficial')?.addEventListener('click', convertirAOficial);
    document.getElementById('btnPdf')?.addEventListener('click', generatePdf);
    document.getElementById('btnModificar')?.addEventListener('click', showModificarModal);
    document.getElementById('btnAceptada')?.addEventListener('click', showAceptadaModal);
    document.getElementById('btnAgregarItem')?.addEventListener('click', addItem);
    document.getElementById('btnCrearCliente')?.addEventListener('click', () => {
        document.getElementById('formNuevoCliente')?.reset();
        new bootstrap.Modal(document.getElementById('modalNuevoCliente')).show();
    });
    document.getElementById('btnGuardarNuevoCliente')?.addEventListener('click', guardarNuevoCliente);

    // =========================
    // INIT
    // =========================
    actualizarEstadoVisual();
    aplicarBloqueoUI();
    attachClienteAutocomplete('cliente_doc');
    attachClienteAutocomplete('cliente_razon_social');
    attachAsesorAutocomplete();
    attachContactoAutocomplete();
    configurarTiempoEntrega();
    addItem();
    inicializarCodigo();

    const cotId = document.getElementById('cotizacion_id')?.value;
    if (cotId) { cargarCotizacion(cotId); } 
    else { esBorrador = true; document.getElementById('estado').value = 'En Proceso'; }

    // =========================
    // METODO DE PAGO
    // =========================
    const tipoProducto = document.getElementById("tipo_producto");
    const formaPago = document.getElementById("forma_pago");
    if (tipoProducto && formaPago) {
        tipoProducto.addEventListener("change", function () {
            let valor = this.value;
            formaPago.innerHTML = '<option value="">-- Seleccione forma de pago --</option>';
            if (valor === "stock") {
                formaPago.innerHTML += '<option value="Efectivo">Efectivo</option><option value="Transferencia">Transferencia</option>';
                formaPago.disabled = false;
            } else if (valor === "pedido") {
                formaPago.innerHTML += '<option value="Transferencia">Transferencia</option>';
                formaPago.value = "Transferencia";
                formaPago.disabled = true;
            } else { formaPago.disabled = false; }
        });
    }

    // =========================
    // TIEMPO DE ENTREGA AUTO
    // =========================
    const tipoEntrega = document.getElementById("tipo_entrega");
    const tiempoEntrega = document.getElementById("tiempo_entrega");
    if (tipoEntrega && tiempoEntrega) {
        tipoEntrega.addEventListener("change", function () {
            let valor = this.value;
            if (valor === "stock") { tiempoEntrega.value = "Inmediata"; }
            else if (valor === "proveedor_inmediato") { tiempoEntrega.value = "2 días hábiles"; }
            else if (valor === "proveedor_variable") {
                let dias = prompt("¿Cuántos días demora el proveedor?");
                if (dias) { dias = parseInt(dias); if (!isNaN(dias)) { tiempoEntrega.value = (dias + 2) + " días hábiles"; } }
            } else { tiempoEntrega.value = ""; }
        });
    }
});