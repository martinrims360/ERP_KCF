// =========================================
// SISTEMA DE NOTIFICACIONES
// =========================================
function mostrarNotificacion(mensaje, tipo = 'exito') {
    let container = document.getElementById('notificacionesContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificacionesContainer';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }
    
    const colores = { exito: '#4CAF50', error: '#f44336', info: '#2196F3', warning: '#ff9800' };
    const iconos = { exito: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    
    const notificacion = document.createElement('div');
    notificacion.style.cssText = `
        background: ${colores[tipo] || colores.exito};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        min-width: 300px;
        max-width: 500px;
        animation: slideIn 0.3s ease;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
    `;
    
    notificacion.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 20px;">${iconos[tipo] || iconos.exito}</span>
            <span style="white-space: pre-line;">${mensaje}</span>
        </div>
        <button style="background:none;border:none;color:white;font-size:20px;cursor:pointer;font-weight:bold;">&times;</button>
    `;
    
    container.appendChild(notificacion);
    
    if (!document.querySelector('#notificacionesStyles')) {
        const styles = document.createElement('style');
        styles.id = 'notificacionesStyles';
        styles.textContent = `
            @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
            @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
        `;
        document.head.appendChild(styles);
    }
    
    const cerrarBtn = notificacion.querySelector('button');
    cerrarBtn.onclick = () => {
        notificacion.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notificacion.remove(), 300);
    };
    
    setTimeout(() => {
        if (notificacion.parentNode) {
            notificacion.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notificacion.remove(), 300);
        }
    }, 4000);
}

// =========================================
// FUNCIONES DE ESCAPE Y VALIDACIÓN
// =========================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function actualizarPlaceholderDocumento(prefix = '') {
    const tipo = document.getElementById(`${prefix}tipo_documento`);
    if (!tipo) return;
    const input = document.getElementById(`${prefix}numero_documento`);
    const label = document.getElementById(`${prefix}label_documento`);
    if (!input) return;

    if (tipo.value === 'RUC') {
        input.placeholder = '11 dígitos';
        input.maxLength = 11;
        if (label) label.innerHTML = 'RUC *:';
    } else if (tipo.value === 'DNI') {
        input.placeholder = '8 dígitos';
        input.maxLength = 8;
        if (label) label.innerHTML = 'DNI *:';
    } else if (tipo.value === 'CE') {
        input.placeholder = '9 dígitos';
        input.maxLength = 9;
        if (label) label.innerHTML = 'CE *:';
    } else {
        input.placeholder = 'Ingrese el número';
        input.maxLength = 20;
        if (label) label.innerHTML = 'Número de Documento *:';
    }
}

function validarNumeroDocumento(input, prefix = '') {
    const tipo = document.getElementById(`${prefix}tipo_documento`);
    if (!tipo) return;
    const limites = { RUC: 11, DNI: 8, CE: 9 };
    const max = limites[tipo.value];
    input.value = input.value.replace(/\D/g, '');
    if (max && input.value.length > max) {
        input.value = input.value.slice(0, max);
        mostrarNotificacion(`El ${tipo.value} solo permite ${max} dígitos como máximo.`, 'warning');
    }
}

// =========================================
// FORMATO DE FECHA Y HORA
// =========================================
function formatearFechaHora(fechaISO) {
    if (!fechaISO) return 'No registrada';
    try {
        const fecha = new Date(fechaISO);
        return fecha.toLocaleString('es-PE', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (e) {
        return 'Fecha inválida';
    }
}

// =========================================
// FUNCIONES PARA EL MODAL REDISEÑADO
// =========================================
function agregarContactoModal(data = {}) {
    const container = document.getElementById('listaContactosModal');
    if (!container) return;
    const div = document.createElement('div');
    div.classList.add('item-agregable');
    div.style.cssText = 'background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; position: relative; border: 1px solid #e9ecef;';
    div.innerHTML = `
        <button type="button" class="btn-eliminar" style="position: absolute; top: 10px; right: 10px; background: #dc3545; color: white; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer;">🗑️</button>
        <div class="row">
            <div class="col-md-6 mb-2"><label style="font-size: 0.75rem; font-weight: 600;">Nombre *</label><input class="form-control" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;" data-field="nombre_contacto" value="${escapeHtml(data.nombre_contacto || '')}"></div>
            <div class="col-md-6 mb-2"><label style="font-size: 0.75rem; font-weight: 600;">Cargo</label><input class="form-control" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;" data-field="cargo" value="${escapeHtml(data.cargo || '')}"></div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-2"><label style="font-size: 0.75rem; font-weight: 600;">Email</label><input class="form-control" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;" data-field="email" value="${escapeHtml(data.email || '')}"></div>
            <div class="col-md-6 mb-2"><label style="font-size: 0.75rem; font-weight: 600;">Teléfono</label><input class="form-control" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;" data-field="telefono" value="${escapeHtml(data.telefono || '')}"></div>
        </div>
        <div class="checkbox-group"><input type="checkbox" data-field="principal" ${data.principal ? 'checked' : ''}> <label style="font-size: 0.75rem; font-weight: 600;">Contacto Principal</label></div>
    `;
    container.appendChild(div);
}

function agregarPuntoModal(data = {}) {
    const container = document.getElementById('listaPuntosModal');
    if (!container) return;
    const div = document.createElement('div');
    div.classList.add('item-agregable');
    div.style.cssText = 'background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; position: relative; border: 1px solid #e9ecef;';
    div.innerHTML = `
        <button type="button" class="btn-eliminar" style="position: absolute; top: 10px; right: 10px; background: #dc3545; color: white; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer;">🗑️</button>
        <div class="row">
            <div class="col-md-6 mb-2"><label style="font-size: 0.75rem; font-weight: 600;">Punto de Entrega *</label><input class="form-control" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;" data-field="nombre_punto" value="${escapeHtml(data.nombre_punto || '')}"></div>
            <div class="col-md-6 mb-2"><label style="font-size: 0.75rem; font-weight: 600;">Dirección</label><input class="form-control" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;" data-field="direccion" value="${escapeHtml(data.direccion || '')}"></div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-2"><label style="font-size: 0.75rem; font-weight: 600;">Contacto de Entrega</label><input class="form-control" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;" data-field="responsable" value="${escapeHtml(data.responsable || '')}"></div>
            <div class="col-md-6 mb-2"><label style="font-size: 0.75rem; font-weight: 600;">Teléfono</label><input class="form-control" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;" data-field="telefono_punto" value="${escapeHtml(data.telefono_punto || '')}"></div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-2">
                <label style="font-size: 0.75rem; font-weight: 600;">Condición de Pago</label>
                <select data-field="condicion_pago" class="form-select select-condicion-pago" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;">
                    <option value="">Seleccione</option>
                    <option value="Contado" ${data.condicion_pago === 'Contado' ? 'selected' : ''}>Contado</option>
                    <option value="Crédito 7 días" ${data.condicion_pago === 'Crédito 7 días' ? 'selected' : ''}>Crédito 7 días</option>
                    <option value="Crédito 15 días" ${data.condicion_pago === 'Crédito 15 días' ? 'selected' : ''}>Crédito 15 días</option>
                    <option value="Crédito 30 días" ${data.condicion_pago === 'Crédito 30 días' ? 'selected' : ''}>Crédito 30 días</option>
                    <option value="Crédito 45 días" ${data.condicion_pago === 'Crédito 45 días' ? 'selected' : ''}>Crédito 45 días</option>
                    <option value="Crédito 60 días" ${data.condicion_pago === 'Crédito 60 días' ? 'selected' : ''}>Crédito 60 días</option>
                    <option value="Crédito 90 días" ${data.condicion_pago === 'Crédito 90 días' ? 'selected' : ''}>Crédito 90 días</option>
                    <option value="Personalizado" ${data.condicion_pago === 'Personalizado' ? 'selected' : ''}>Personalizado (escribir)</option>
                </select>
            </div>
            <div class="col-md-6 mb-2 campo-credito-personalizado" style="display: ${data.condicion_pago === 'Personalizado' ? 'block' : 'none'};">
                <label style="font-size: 0.75rem; font-weight: 600;">Escribir condición</label>
                <input type="text" class="form-control" style="border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.9rem; padding: 0.5rem 0.75rem;" data-field="tiempo_credito" placeholder="Ej: Crédito 20 días..." value="${escapeHtml(data.tiempo_credito || '')}">
            </div>
        </div>
        <div class="checkbox-group"><input type="checkbox" data-field="principal_punto" ${data.principal_punto ? 'checked' : ''}> <label style="font-size: 0.75rem; font-weight: 600;">Punto Principal</label></div>
    `;
    container.appendChild(div);
    
    const selectCondicion = div.querySelector('.select-condicion-pago');
    const campoPersonalizado = div.querySelector('.campo-credito-personalizado');
    if (selectCondicion && campoPersonalizado) {
        selectCondicion.addEventListener('change', function() {
            campoPersonalizado.style.display = this.value === 'Personalizado' ? 'block' : 'none';
        });
    }
}

function obtenerContactosModal() {
    const contactos = [];
    document.querySelectorAll('#listaContactosModal .item-agregable').forEach(item => {
        const nombre = item.querySelector('[data-field="nombre_contacto"]')?.value.trim();
        if (nombre) {
            contactos.push({
                nombre_contacto: nombre,
                cargo: item.querySelector('[data-field="cargo"]')?.value.trim() || '',
                email: item.querySelector('[data-field="email"]')?.value.trim() || '',
                telefono: item.querySelector('[data-field="telefono"]')?.value.trim() || '',
                principal: item.querySelector('[data-field="principal"]')?.checked || false
            });
        }
    });
    return contactos;
}

function obtenerPuntosModal() {
    const puntos = [];
    document.querySelectorAll('#listaPuntosModal .item-agregable').forEach(item => {
        const nombre = item.querySelector('[data-field="nombre_punto"]')?.value.trim();
        if (nombre) {
            const condicionPago = item.querySelector('[data-field="condicion_pago"]')?.value || '';
            const tiempoCredito = item.querySelector('[data-field="tiempo_credito"]')?.value.trim() || '';
            puntos.push({
                nombre_punto: nombre,
                direccion: item.querySelector('[data-field="direccion"]')?.value.trim() || '',
                responsable: item.querySelector('[data-field="responsable"]')?.value.trim() || '',
                telefono: item.querySelector('[data-field="telefono_punto"]')?.value.trim() || '',
                condicion_pago: condicionPago === 'Personalizado' ? tiempoCredito : condicionPago,
                tiempo_credito: condicionPago === 'Personalizado' ? '' : tiempoCredito,
                principal: item.querySelector('[data-field="principal_punto"]')?.checked || false
            });
        }
    });
    return puntos;
}

// =========================================
// CONSULTAR SUNAT MODAL
// =========================================
async function consultarSunatModal() {
    const tipoDoc = document.getElementById('tipo_documento_modal').value;
    const numDoc = document.getElementById('numero_documento_modal').value;
    const resultadoSpan = document.getElementById('sunat-resultado-modal');

    if (tipoDoc !== 'RUC') {
        mostrarNotificacion('⚠️ La consulta a SUNAT solo está disponible para RUC', 'warning');
        return;
    }
    if (!numDoc || numDoc.length !== 11) {
        mostrarNotificacion('Ingrese un RUC válido de 11 dígitos', 'warning');
        return;
    }

    const btn = document.getElementById('btnConsultarSunatModal');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Consultando...';
    btn.disabled = true;
    resultadoSpan.innerHTML = '<i class="bi bi-hourglass-split text-info"></i> Consultando SUNAT...';

    try {
        const response = await fetch(`/api/sunat/consulta?ruc=${numDoc}`);
        const data = await response.json();
        if (data.success) {
            if (data.razon_social) document.getElementById('razon_social_modal').value = data.razon_social;
            if (data.nombre_comercial) document.getElementById('nombre_comercial_modal').value = data.nombre_comercial;
            if (data.direccion) document.getElementById('direccion_fiscal_modal').value = data.direccion;
            resultadoSpan.innerHTML = `<i class="bi bi-check-circle-fill text-success"></i> ✅ Datos cargados desde SUNAT: ${data.razon_social}`;
            mostrarNotificacion(`✅ Datos cargados desde SUNAT: ${data.razon_social}`, 'exito');
            setTimeout(() => { resultadoSpan.innerHTML = 'Ingrese el RUC y presione buscar para autocompletar los datos del cliente desde SUNAT'; }, 5000);
        } else {
            const errorMsg = data.error || 'No se encontraron datos para este RUC';
            resultadoSpan.innerHTML = `<i class="bi bi-exclamation-triangle-fill text-danger"></i> ❌ ${errorMsg}`;
            mostrarNotificacion(`❌ ${errorMsg}`, 'error');
            setTimeout(() => { resultadoSpan.innerHTML = 'Ingrese el RUC y presione buscar para autocompletar los datos del cliente desde SUNAT'; }, 5000);
        }
    } catch (error) {
        resultadoSpan.innerHTML = `<i class="bi bi-exclamation-triangle-fill text-danger"></i> Error de conexión`;
        mostrarNotificacion(`❌ Error al consultar SUNAT`, 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// =========================================
// CARGAR CLIENTES
// =========================================
let timeoutBusqueda = null;

async function cargarClientes(filtros = {}) {
    const tbody = document.getElementById("tbody-clientes");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="10" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <br>Cargando clientes...
    </td></tr>`;

    try {
        let url = "/api/clientes/buscar";
        const params = new URLSearchParams();

        if (filtros.tipo) params.append("tipo_documento", filtros.tipo);
        if (filtros.busqueda && filtros.busqueda.trim()) {
            params.append("busqueda", filtros.busqueda.trim());
        }

        if (params.toString()) url += "?" + params.toString();

        const res = await fetch(url);
        const json = await res.json();

        if (!json.success) {
            throw new Error(json.error || "Error al cargar clientes");
        }

        const clientes = json.data || [];

        tbody.innerHTML = "";

        if (clientes.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-muted">
                <i class="bi bi-search" style="font-size: 3rem;"></i><br>
                No se encontraron resultados
            </td></tr>`;
            return;
        }

        clientes.forEach(c => {
            const contactos = (c.contactos?.length) 
                ? c.contactos.map(ct => `📞 ${escapeHtml(ct.nombre_contacto || '')}`).join('<br>') 
                : '<em class="text-muted">Sin contactos</em>';

            const puntos = (c.puntos_entrega?.length) 
                ? c.puntos_entrega.map(p => `📦 ${escapeHtml(p.nombre_punto || '')}`).join('<br>') 
                : '<em class="text-muted">Sin puntos</em>';

            const condicionPago = c.puntos_entrega?.[0]?.condicion_pago || '-';
            const codigoCliente = c.codigo_cliente || '---';

            tbody.innerHTML += `
                <tr>
                    <td class="text-center">${c.id || '-'}</td>
                    <td class="text-center"><span class="badge bg-secondary">${escapeHtml(codigoCliente)}</span></td>
                    <td><strong>${escapeHtml(c.nombre_comercial) || '-'}</strong></td>
                    <td>${escapeHtml(c.razon_social) || '-'}</td>
                    <td class="text-center"><span class="badge bg-info">${c.numero_documento || '-'}</span></td>
                    <td>${escapeHtml(c.direccion_fiscal) || '-'}</td>
                    <td class="text-center">${condicionPago}</td>
                    <td>${contactos}</td>
                    <td>${puntos}</td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-primary me-1" onclick="abrirModalVer(${c.id})" title="Ver cliente">
                            <i class="bi bi-eye-fill"></i> Ver
                        </button>
                        <button class="btn btn-sm btn-warning me-1" onclick="abrirModalEditar(${c.id})" title="Editar cliente">
                            <i class="bi bi-pencil-fill"></i> Editar
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="abrirModalEliminar(${c.id})" title="Eliminar cliente">
                            <i class="bi bi-trash-fill"></i> Eliminar
                        </button>
                    </td>
                </tr>
            `;
        });

    } catch (e) {
        console.error("Error:", e);
        tbody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-danger">
            Error al cargar clientes: ${e.message}
        </td></tr>`;
    }
}

// =========================================
// INICIALIZAR FILTROS
// =========================================
function inicializarFiltros() {
    const filtroTipo = document.getElementById("filtro-tipo");
    const filtroBusqueda = document.getElementById("filtro-busqueda");

    if (filtroTipo) {
        filtroTipo.addEventListener("change", () => aplicarFiltros());
    }

    if (filtroBusqueda) {
        filtroBusqueda.addEventListener("input", () => {
            clearTimeout(timeoutBusqueda);
            timeoutBusqueda = setTimeout(aplicarFiltros, 500);
        });

        filtroBusqueda.addEventListener("keypress", (e) => {
            if (e.key === "Enter") aplicarFiltros();
        });
    }
}

function aplicarFiltros() {
    const tipo = document.getElementById("filtro-tipo")?.value || "";
    const busqueda = document.getElementById("filtro-busqueda")?.value || "";
    cargarClientes({ tipo, busqueda });
}

// =========================================
// ABRIR MODAL VER CLIENTE
// =========================================
window.abrirModalVer = async function(id) {
    if (!id) {
        mostrarNotificacion("ID de cliente no válido", 'error');
        return;
    }
    
    const modalBody = document.getElementById('modalVerBody');
    if (!modalBody) {
        mostrarNotificacion("Modal de visualización no encontrado", 'error');
        return;
    }
    
    modalBody.innerHTML = `<div class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-2">Cargando datos del cliente...</p></div>`;
    
    try {
        const res = await fetch(`/api/clientes/${id}`);
        const json = await res.json();
        
        if (!json.success || !json.data) {
            throw new Error(json.error || "Error al cargar los datos");
        }
        
        const c = json.data;
        const fechaRegistro = formatearFechaHora(c.created_at || c.fecha_registro);
        const codigoCliente = c.codigo_cliente || '---';
        
        let html = `
            <div class="row g-4 mb-4">
                <div class="col-md-6">
                    <div class="card bg-gradient-primary text-white text-center p-4 rounded-4 shadow-sm" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        <i class="bi bi-upc-scan" style="font-size: 2.5rem;"></i>
                        <h6 class="text-uppercase mt-2 mb-1 opacity-75">Código de Cliente</h6>
                        <h2 class="fw-bold mb-0">${escapeHtml(codigoCliente)}</h2>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card bg-gradient-info text-white text-center p-4 rounded-4 shadow-sm" style="background: linear-gradient(135deg, #0dcaf0 0%, #0d6efd 100%);">
                        <i class="bi bi-calendar-clock-fill" style="font-size: 2.5rem;"></i>
                        <h6 class="text-uppercase mt-2 mb-1 opacity-75">Fecha y Hora de Registro</h6>
                        <h2 class="fw-bold mb-0" style="font-size: 1.2rem;">${fechaRegistro}</h2>
                    </div>
                </div>
            </div>
        `;
        
        html += `
            <div class="erp-section-title mt-2 mb-3">
                <i class="bi bi-info-circle-fill"></i> Información General
            </div>
            <div class="row g-3">
                <div class="col-md-6">
                    <div class="info-row-ver">
                        <div class="info-label-ver">TIPO DOCUMENTO</div>
                        <div class="info-value-ver">${escapeHtml(c.tipo_documento || '-')}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-row-ver">
                        <div class="info-label-ver">NÚMERO DE DOCUMENTO</div>
                        <div class="info-value-ver"><strong>${escapeHtml(c.numero_documento || '-')}</strong></div>
                    </div>
                </div>
                <div class="col-md-12">
                    <div class="info-row-ver">
                        <div class="info-label-ver">RAZÓN SOCIAL</div>
                        <div class="info-value-ver">${escapeHtml(c.razon_social || '-')}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-row-ver">
                        <div class="info-label-ver">NOMBRE COMERCIAL</div>
                        <div class="info-value-ver">${escapeHtml(c.nombre_comercial || '-')}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-row-ver">
                        <div class="info-label-ver">DIRECCIÓN FISCAL</div>
                        <div class="info-value-ver">${escapeHtml(c.direccion_fiscal || '-')}</div>
                    </div>
                </div>
            </div>
        `;
        
        html += `<div class="erp-section-title mt-4 mb-3"><i class="bi bi-person-badge"></i> Contactos Asociados</div>`;
        if (c.contactos && c.contactos.length > 0) {
            c.contactos.forEach(contacto => {
                html += `
                    <div class="contact-card-ver">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${escapeHtml(contacto.nombre_contacto || 'Sin nombre')}</strong>
                                ${contacto.principal ? '<span class="badge-principal ms-2"><i class="bi bi-star-fill"></i> Principal</span>' : ''}
                                <div class="small text-muted mt-1">
                                    ${contacto.cargo ? `<i class="bi bi-briefcase"></i> ${escapeHtml(contacto.cargo)}<br>` : ''}
                                    ${contacto.email ? `<i class="bi bi-envelope"></i> ${escapeHtml(contacto.email)}<br>` : ''}
                                    ${contacto.telefono ? `<i class="bi bi-telephone"></i> ${escapeHtml(contacto.telefono)}` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        } else {
            html += `<p class="text-muted">No hay contactos registrados</p>`;
        }
        
        html += `<div class="erp-section-title mt-4 mb-3"><i class="bi bi-geo-alt-fill"></i> Puntos de Entrega</div>`;
        if (c.puntos_entrega && c.puntos_entrega.length > 0) {
            c.puntos_entrega.forEach(punto => {
                html += `
                    <div class="punto-card-ver">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${escapeHtml(punto.nombre_punto || 'Sin nombre')}</strong>
                                ${punto.principal_punto ? '<span class="badge-principal ms-2"><i class="bi bi-star-fill"></i> Principal</span>' : ''}
                                <div class="small text-muted mt-1">
                                    ${punto.direccion ? `<i class="bi bi-pin-map"></i> ${escapeHtml(punto.direccion)}<br>` : ''}
                                    ${punto.responsable ? `<i class="bi bi-person"></i> Contacto: ${escapeHtml(punto.responsable)}<br>` : ''}
                                    ${punto.telefono_punto ? `<i class="bi bi-telephone"></i> ${escapeHtml(punto.telefono_punto)}<br>` : ''}
                                    ${punto.condicion_pago ? `<i class="bi bi-credit-card"></i> Condición: <strong>${escapeHtml(punto.condicion_pago)}</strong>` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        } else {
            html += `<p class="text-muted">No hay puntos de entrega registrados</p>`;
        }
        
        modalBody.innerHTML = html;
        const modalElement = document.getElementById('modalVerCliente');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
        
    } catch (error) {
        console.error("Error al cargar cliente:", error);
        modalBody.innerHTML = `<div class="text-center py-5 text-danger">
            <i class="bi bi-exclamation-triangle-fill" style="font-size: 3rem;"></i>
            <p class="mt-2">Error al cargar los datos: ${error.message}</p>
        </div>`;
        mostrarNotificacion("Error cargando cliente: " + error.message, 'error');
    }
};

// =========================================
// ABRIR MODAL EDITAR
// =========================================
window.abrirModalEditar = async function(id) {
    if (!id) {
        mostrarNotificacion("ID de cliente no válido", 'error');
        return;
    }
    
    try {
        mostrarNotificacion("Cargando datos del cliente...", 'info');
        
        const res = await fetch(`/api/clientes/${id}`);
        const json = await res.json();
        
        if (!json.success || !json.data) {
            throw new Error(json.error || "Error al cargar los datos");
        }
        
        const c = json.data;
        
        document.getElementById('edit_listaContactos').innerHTML = '';
        document.getElementById('edit_listaPuntos').innerHTML = '';
        
        document.getElementById('edit_id').value = c.id;
        document.getElementById('edit_tipo_documento').value = c.tipo_documento || '';
        document.getElementById('edit_numero_documento').value = c.numero_documento || '';
        document.getElementById('edit_razon_social').value = c.razon_social || '';
        document.getElementById('edit_nombre_comercial').value = c.nombre_comercial || '';
        document.getElementById('edit_direccion_fiscal').value = c.direccion_fiscal || '';
        actualizarPlaceholderDocumento('edit_');
        
        function agregarContactoEdicion(data) {
            const container = document.getElementById('edit_listaContactos');
            const div = document.createElement('div');
            div.classList.add('item-agregable');
            div.style.cssText = 'border:1px solid #ddd;padding:15px;margin-bottom:15px;border-radius:8px;position:relative;background:#f9f9f9;';
            div.innerHTML = `<button type="button" class="btn-eliminar" style="position:absolute;top:10px;right:10px;background:#ff4444;color:white;border:none;border-radius:50%;width:30px;height:30px;cursor:pointer;">🗑️</button>
                <div class="row"><div class="col-md-6 mb-3"><label>Nombre</label><input class="form-control" data-field="edit_nombre_contacto" value="${escapeHtml(data.nombre_contacto || '')}"></div>
                <div class="col-md-6 mb-3"><label>Cargo</label><input class="form-control" data-field="edit_cargo" value="${escapeHtml(data.cargo || '')}"></div></div>
                <div class="row"><div class="col-md-6 mb-3"><label>Email</label><input class="form-control" data-field="edit_email" value="${escapeHtml(data.email || '')}"></div>
                <div class="col-md-6 mb-3"><label>Teléfono</label><input class="form-control" data-field="edit_telefono" value="${escapeHtml(data.telefono || '')}"></div></div>
                <div class="checkbox-group"><input type="checkbox" data-field="principal" ${data.principal ? 'checked' : ''}> <label>Principal</label></div>`;
            container.appendChild(div);
        }
        
        function agregarPuntoEdicion(data) {
            const container = document.getElementById('edit_listaPuntos');
            const div = document.createElement('div');
            div.classList.add('item-agregable');
            div.style.cssText = 'border:1px solid #ddd;padding:15px;margin-bottom:15px;border-radius:8px;position:relative;background:#f9f9f9;';
            div.innerHTML = `<button type="button" class="btn-eliminar" style="position:absolute;top:10px;right:10px;background:#ff4444;color:white;border:none;border-radius:50%;width:30px;height:30px;cursor:pointer;">🗑️</button>
                <div class="row"><div class="col-md-6 mb-3"><label>Punto de Entrega</label><input class="form-control" data-field="edit_nombre_punto" value="${escapeHtml(data.nombre_punto || '')}"></div>
                <div class="col-md-6 mb-3"><label>Dirección</label><input class="form-control" data-field="edit_direccion" value="${escapeHtml(data.direccion || '')}"></div></div>
                <div class="row"><div class="col-md-6 mb-3"><label>Contacto de Entrega</label><input class="form-control" data-field="edit_responsable" value="${escapeHtml(data.responsable || '')}"></div>
                <div class="col-md-6 mb-3"><label>Teléfono</label><input class="form-control" data-field="edit_telefono_punto" value="${escapeHtml(data.telefono_punto || '')}"></div></div>
                <div class="row"><div class="col-md-6 mb-3"><label>Condición de Pago</label>
                    <select data-field="edit_condicion_pago" class="form-select select-condicion-pago">
                        <option value="">Seleccione</option>
                        <option value="Contado" ${data.condicion_pago === 'Contado' ? 'selected' : ''}>Contado</option>
                        <option value="Crédito 7 días" ${data.condicion_pago === 'Crédito 7 días' ? 'selected' : ''}>Crédito 7 días</option>
                        <option value="Crédito 15 días" ${data.condicion_pago === 'Crédito 15 días' ? 'selected' : ''}>Crédito 15 días</option>
                        <option value="Crédito 30 días" ${data.condicion_pago === 'Crédito 30 días' ? 'selected' : ''}>Crédito 30 días</option>
                        <option value="Crédito 45 días" ${data.condicion_pago === 'Crédito 45 días' ? 'selected' : ''}>Crédito 45 días</option>
                        <option value="Crédito 60 días" ${data.condicion_pago === 'Crédito 60 días' ? 'selected' : ''}>Crédito 60 días</option>
                        <option value="Crédito 90 días" ${data.condicion_pago === 'Crédito 90 días' ? 'selected' : ''}>Crédito 90 días</option>
                        <option value="Personalizado" ${data.condicion_pago === 'Personalizado' ? 'selected' : ''}>Personalizado (escribir)</option>
                    </select>
                </div>
                <div class="col-md-6 mb-3 campo-credito-personalizado" style="display:${data.condicion_pago === 'Personalizado' ? 'block' : 'none'}">
                    <label>Escribir condición</label><input type="text" class="form-control" data-field="edit_tiempo_credito" placeholder="Ej: Crédito 20 días..." value="${escapeHtml(data.tiempo_credito || '')}">
                </div></div>
                <div class="checkbox-group"><input type="checkbox" data-field="principal_punto" ${data.principal_punto ? 'checked' : ''}> <label>Principal</label></div>`;
            container.appendChild(div);
            const selectCondicion = div.querySelector('.select-condicion-pago');
            const campoPersonalizado = div.querySelector('.campo-credito-personalizado');
            if (selectCondicion && campoPersonalizado) {
                selectCondicion.addEventListener('change', function() {
                    campoPersonalizado.style.display = this.value === 'Personalizado' ? 'block' : 'none';
                });
            }
        }
        
        if (c.contactos && c.contactos.length > 0) {
            c.contactos.forEach(contacto => agregarContactoEdicion(contacto));
        } else {
            agregarContactoEdicion({});
        }
        
        if (c.puntos_entrega && c.puntos_entrega.length > 0) {
            c.puntos_entrega.forEach(punto => agregarPuntoEdicion(punto));
        } else {
            agregarPuntoEdicion({});
        }
        
        const modal = new bootstrap.Modal(document.getElementById('modalEditarCliente'));
        modal.show();
        
    } catch (error) {
        console.error("Error al cargar cliente para editar:", error);
        mostrarNotificacion("Error cargando cliente: " + error.message, 'error');
    }
};

// =========================================
// GUARDAR EDICIÓN
// =========================================
document.getElementById('formEditarCliente')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const id = document.getElementById('edit_id').value;
    if (!id) {
        mostrarNotificacion("ID no encontrado", 'error');
        return;
    }
    
    const tipoDoc = document.getElementById('edit_tipo_documento').value;
    const numDoc = document.getElementById('edit_numero_documento').value;
    const razonSocial = document.getElementById('edit_razon_social').value;
    
    if (!tipoDoc) {
        mostrarNotificacion("Seleccione el tipo de documento", 'error');
        return;
    }
    if (!numDoc) {
        mostrarNotificacion("Ingrese el número de documento", 'error');
        return;
    }
    if (!razonSocial) {
        mostrarNotificacion("Ingrese la razón social", 'error');
        return;
    }
    
    const data = {
        tipo_documento: tipoDoc,
        numero_documento: numDoc,
        razon_social: razonSocial,
        nombre_comercial: document.getElementById('edit_nombre_comercial').value,
        direccion_fiscal: document.getElementById('edit_direccion_fiscal').value,
        contactos: [],
        puntos_entrega: []
    };
    
    document.querySelectorAll('#edit_listaContactos .item-agregable').forEach(item => {
        const nombreContacto = item.querySelector('[data-field="edit_nombre_contacto"]')?.value.trim();
        if (nombreContacto) {
            data.contactos.push({
                nombre_contacto: nombreContacto,
                cargo: item.querySelector('[data-field="edit_cargo"]')?.value.trim() || '',
                email: item.querySelector('[data-field="edit_email"]')?.value.trim() || '',
                telefono: item.querySelector('[data-field="edit_telefono"]')?.value.trim() || '',
                principal: item.querySelector('[data-field="principal"]')?.checked || false
            });
        }
    });
    
    document.querySelectorAll('#edit_listaPuntos .item-agregable').forEach(item => {
        const nombrePunto = item.querySelector('[data-field="edit_nombre_punto"]')?.value.trim();
        if (nombrePunto) {
            const condicionPago = item.querySelector('[data-field="edit_condicion_pago"]')?.value || '';
            const tiempoCredito = item.querySelector('[data-field="edit_tiempo_credito"]')?.value.trim() || '';
            data.puntos_entrega.push({
                nombre_punto: nombrePunto,
                direccion: item.querySelector('[data-field="edit_direccion"]')?.value.trim() || '',
                responsable: item.querySelector('[data-field="edit_responsable"]')?.value.trim() || '',
                telefono: item.querySelector('[data-field="edit_telefono_punto"]')?.value.trim() || '',
                condicion_pago: condicionPago === 'Personalizado' ? tiempoCredito : condicionPago,
                tiempo_credito: condicionPago === 'Personalizado' ? '' : tiempoCredito,
                principal: item.querySelector('[data-field="principal_punto"]')?.checked || false
            });
        }
    });
    
    try {
        const res = await fetch(`/api/clientes/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const json = await res.json();
        
        if (json.success) {
            bootstrap.Modal.getInstance(document.getElementById('modalEditarCliente'))?.hide();
            await cargarClientes();
            mostrarNotificacion("✅ Cliente actualizado correctamente", 'exito');
        } else {
            mostrarNotificacion("❌ Error: " + json.error, 'error');
        }
    } catch (error) {
        console.error("Error al actualizar:", error);
        mostrarNotificacion("Error al actualizar: " + error.message, 'error');
    }
});

// =========================================
// GUARDAR NUEVO CLIENTE (MODAL REDISEÑADO)
// =========================================
document.getElementById('formCliente')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const btnGuardar = document.getElementById('btnGuardarClienteModal');
    const textoOriginal = btnGuardar?.innerHTML || 'Guardar';
    if (btnGuardar) {
        btnGuardar.disabled = true;
        btnGuardar.innerHTML = '<i class="bi bi-hourglass-split"></i> Guardando...';
    }

    try {
        const contactos = obtenerContactosModal();
        const puntos = obtenerPuntosModal();
        
        if (contactos.length === 0) {
            mostrarNotificacion("Agregue al menos un contacto", 'error');
            if (btnGuardar) { btnGuardar.disabled = false; btnGuardar.innerHTML = textoOriginal; }
            return;
        }
        if (puntos.length === 0) {
            mostrarNotificacion("Agregue al menos un punto de entrega", 'error');
            if (btnGuardar) { btnGuardar.disabled = false; btnGuardar.innerHTML = textoOriginal; }
            return;
        }

        const data = {
            tipo_documento: document.getElementById('tipo_documento_modal').value,
            numero_documento: document.getElementById('numero_documento_modal').value,
            razon_social: document.getElementById('razon_social_modal').value,
            nombre_comercial: document.getElementById('nombre_comercial_modal').value,
            direccion_fiscal: document.getElementById('direccion_fiscal_modal').value,
            contactos: contactos,
            puntos_entrega: puntos
        };

        if (!data.razon_social) {
            mostrarNotificacion("La Razón Social es obligatoria", 'error');
            if (btnGuardar) { btnGuardar.disabled = false; btnGuardar.innerHTML = textoOriginal; }
            return;
        }
        if (!data.numero_documento) {
            mostrarNotificacion("El número de documento es obligatorio", 'error');
            if (btnGuardar) { btnGuardar.disabled = false; btnGuardar.innerHTML = textoOriginal; }
            return;
        }

        const res = await fetch('/api/clientes/guardar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const json = await res.json();

        if (json.success) {
            mostrarNotificacion("✅ Cliente guardado correctamente", 'exito');
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalCliente'));
            if (modal) modal.hide();
            document.getElementById('formCliente').reset();
            document.getElementById('listaContactosModal').innerHTML = '';
            document.getElementById('listaPuntosModal').innerHTML = '';
            agregarContactoModal();
            agregarPuntoModal();
            cargarClientes();
        } else {
            mostrarNotificacion("❌ " + (json.error || "Error al guardar el cliente"), 'error');
        }
    } catch (error) {
        console.error(error);
        mostrarNotificacion("❌ Error de conexión: " + error.message, 'error');
    } finally {
        if (btnGuardar) {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = textoOriginal;
        }
    }
});

// =========================================
// ELIMINAR CLIENTE
// =========================================
window.abrirModalEliminar = function(id) {
    if (!id) return;
    document.getElementById('delete_id').value = id;
    const modal = new bootstrap.Modal(document.getElementById('modalEliminarCliente'));
    modal.show();
};

document.getElementById('btnConfirmarEliminar')?.addEventListener('click', async function() {
    const id = document.getElementById('delete_id').value;
    if (!id) return;
    
    try {
        const res = await fetch(`/api/clientes/${id}`, { method: 'DELETE' });
        const json = await res.json();
        
        if (json.success) {
            mostrarNotificacion(`✅ Cliente eliminado exitosamente`, 'exito');
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalEliminarCliente'));
            if (modal) modal.hide();
            await cargarClientes();
        } else {
            mostrarNotificacion("❌ Error: " + json.error, 'error');
        }
    } catch (error) {
        console.error("Error al eliminar:", error);
        mostrarNotificacion("Error al eliminar: " + error.message, 'error');
    }
});

// =========================================
// INICIALIZACIÓN
// =========================================
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Inicializando sistema de gestión de clientes...");
    cargarClientes();
    inicializarFiltros();
    
    // Configurar eventos del modal rediseñado
    const btnConsultarSunat = document.getElementById('btnConsultarSunatModal');
    if (btnConsultarSunat) {
        btnConsultarSunat.addEventListener('click', consultarSunatModal);
    }
    
    const btnLimpiarSunat = document.getElementById('btnLimpiarSunatModal');
    if (btnLimpiarSunat) {
        btnLimpiarSunat.addEventListener('click', () => {
            document.getElementById('numero_documento_modal').value = '';
            document.getElementById('razon_social_modal').value = '';
            document.getElementById('nombre_comercial_modal').value = '';
            document.getElementById('direccion_fiscal_modal').value = '';
            document.getElementById('correo_modal').value = '';
            mostrarNotificacion('Formulario limpiado', 'info');
        });
    }
    
    const btnAgregarContacto = document.getElementById('btnAgregarContactoModal');
    if (btnAgregarContacto) {
        btnAgregarContacto.addEventListener('click', () => agregarContactoModal());
    }
    
    const btnAgregarPunto = document.getElementById('btnAgregarPuntoModal');
    if (btnAgregarPunto) {
        btnAgregarPunto.addEventListener('click', () => agregarPuntoModal());
    }
    
    // Manejar eliminación de items
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-eliminar')) {
            e.target.closest('.item-agregable').remove();
        }
    });
    
    // Solo un principal por sección
    document.addEventListener('change', (e) => {
        if (e.target.dataset.field === 'principal') {
            const container = document.getElementById('listaContactosModal');
            if (container) {
                const checkboxes = container.querySelectorAll('[data-field="principal"]');
                checkboxes.forEach(cb => { if (cb !== e.target) cb.checked = false; });
            }
        }
        if (e.target.dataset.field === 'principal_punto') {
            const container = document.getElementById('listaPuntosModal');
            if (container) {
                const checkboxes = container.querySelectorAll('[data-field="principal_punto"]');
                checkboxes.forEach(cb => { if (cb !== e.target) cb.checked = false; });
            }
        }
    });
    
    // Inicializar con un contacto y un punto por defecto
    setTimeout(() => {
        if (document.getElementById('listaContactosModal')?.children.length === 0) {
            agregarContactoModal();
        }
        if (document.getElementById('listaPuntosModal')?.children.length === 0) {
            agregarPuntoModal();
        }
    }, 100);
});