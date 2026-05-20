document.addEventListener("DOMContentLoaded", () => {
    cargarProveedores();
});

async function cargarProveedores() {
    const tbody = document.getElementById("tbody-proveedores");

    try {
        const res = await fetch("/api/proveedores");
        const json = await res.json();

        const proveedores = json.data || [];

        tbody.innerHTML = "";

        proveedores.forEach(p => {

            const fila = `
                <tr>
                    <td>${ p.id }</td>
                    <td>${ p.codigo_proveedor }</td>
                    <td>${p.razon_social}</td>
                    <td>${p.ruc}</td>
                    <td>${p.direccion || '-'}</td>
                    <td>${p.telefono || '-'}</td>
                    <td>${p.contacto || '-'}</td>
                    <td>${p.email || '-'}</td>
                    <td>${p.razon_comercial || '-'}</td>
                    <td>
                        <button onclick="editarProveedor(${p.id})">✏️</button>
                        <button onclick="eliminarProveedor(${p.id})">🗑️</button>
                    </td>
                </tr>
            `;

            tbody.innerHTML += fila;
        });

    } catch (error) {
        console.error("Error:", error);
    }
}

function editarProveedor(id) {
    window.location.href = `/mantenedor/proveedores/editar/${id}`;
}

function eliminarProveedor(id) {
    if (!confirm("¿Eliminar proveedor?")) return;

    fetch(`/api/proveedores/${id}`, {
        method: "DELETE"
    }).then(() => cargarProveedores());
}