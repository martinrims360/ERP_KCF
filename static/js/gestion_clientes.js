// =========================================
// INICIAL
// =========================================
document.addEventListener("DOMContentLoaded", () => {

    cargarClientes();

    inicializarFormularioCliente();

    inicializarEventosUI();

});

// =========================================
// LISTAR CLIENTES
// =========================================
async function cargarClientes() {

    const tbody = document.getElementById("tbody-clientes");

    try {

        const res = await fetch("/api/clientes/buscar");
        const json = await res.json();
        const clientes = json.data || [];

        tbody.innerHTML = "";

        clientes.forEach(c => {

            const contactos = (c.contactos?.length)
                ? c.contactos.map(ct => `📞 ${ct.nombre_contacto}`).join('<br>')
                : '<em>Sin contactos</em>';

            const puntos = (c.puntos_entrega?.length)
                ? c.puntos_entrega.map(p => `📦 ${p.nombre_punto}`).join('<br>')
                : '<em>Sin puntos</em>';

            const condicionPago = c.puntos_entrega?.[0]?.condicion_pago || '-';

            tbody.innerHTML += `
                <tr>
                    <td>${c.id}</td>
                    <td>${c.codigo_cliente || '-'}</td>
                    <td>${c.nombre_comercial || '-'}</td>
                    <td>${c.razon_social || '-'}</td>
                    <td>${c.numero_documento || '-'}</td>
                    <td>${c.direccion_fiscal || '-'}</td>
                    <td>${condicionPago}</td>
                    <td>${contactos}</td>
                    <td>${puntos}</td>
                    <td>
                        <button class="btn-action btn-edit"
                            onclick="abrirModalEditar(${c.id})">✏️</button>

                        <button class="btn-action btn-delete"
                            onclick="abrirModalEliminar(${c.id})">🗑️</button>
                    </td>
                </tr>
            `;
        });

    } catch (e) {
        console.error(e);
    }
}


// =========================================
// ABRIR MODAL EDITAR
// =========================================
async function abrirModalEditar(id) {

    try {

        const res = await fetch(`/api/clientes/${id}`);
        const json = await res.json();
        const c = json.data;

        document.getElementById('edit_id').value = c.id;
        document.getElementById('edit_numero_documento').value = c.numero_documento || '';
        document.getElementById('edit_razon_social').value = c.razon_social || '';
        document.getElementById('edit_nombre_comercial').value = c.nombre_comercial || '';
        document.getElementById('edit_direccion_fiscal').value = c.direccion_fiscal || '';

        const modal = new bootstrap.Modal(
            document.getElementById('modalEditarCliente')
        );

        modal.show();

    } catch (error) {
        console.error(error);
        alert("Error cargando cliente");
    }
}


// =========================================
// GUARDAR EDICIÓN
// =========================================
document.getElementById('formEditarCliente')
.addEventListener('submit', async function (e) {

    e.preventDefault();

    const id = document.getElementById('edit_id').value;

    const data = {
        numero_documento: document.getElementById('edit_numero_documento').value,
        razon_social: document.getElementById('edit_razon_social').value,
        nombre_comercial: document.getElementById('edit_nombre_comercial').value,
        direccion_fiscal: document.getElementById('edit_direccion_fiscal').value
    };

    try {

        const res = await fetch(`/api/clientes/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const json = await res.json();

        if (json.success) {

            alert("Cliente actualizado");

            bootstrap.Modal.getInstance(
                document.getElementById('modalEditarCliente')
            ).hide();

            cargarClientes();

        } else {
            alert(json.error);
        }

    } catch (error) {
        console.error(error);
        alert("Error actualizando");
    }

});


// =========================================
// ABRIR MODAL ELIMINAR
// =========================================
function abrirModalEliminar(id) {

    document.getElementById('delete_id').value = id;

    const modal = new bootstrap.Modal(
        document.getElementById('modalEliminarCliente')
    );

    modal.show();
}


// (COMPATIBILIDAD) por si en otro lado llamas eliminarCliente
function eliminarCliente(id) {
    abrirModalEliminar(id);
}


// =========================================
// CONFIRMAR ELIMINAR
// =========================================
document.getElementById('btnConfirmarEliminar')
.addEventListener('click', async function () {

    const id = document.getElementById('delete_id').value;

    try {

        const res = await fetch(`/api/clientes/${id}`, {
            method: 'DELETE'
        });

        const json = await res.json();

        if (json.success) {

            alert("Cliente eliminado");

            bootstrap.Modal.getInstance(
                document.getElementById('modalEliminarCliente')
            ).hide();

            cargarClientes();

        } else {
            alert(json.error);
        }

    } catch (error) {
        console.error(error);
        alert("Error eliminando");
    }

});

