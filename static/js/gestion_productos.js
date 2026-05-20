const filtroFamilia = document.getElementById('filtro-familia');
const filtroBusqueda = document.getElementById('filtro-busqueda');

filtroFamilia.addEventListener('change', filtrarProductos);
filtroBusqueda.addEventListener('input', filtrarProductos);

function filtrarProductos() {

    const familia = filtroFamilia.value.toLowerCase();
    const busqueda = filtroBusqueda.value.toLowerCase();

    const filas = document.querySelectorAll('#tabla-productos tbody tr');

    filas.forEach(fila => {

        const filaFamilia =
            (fila.dataset.familia || '').toLowerCase();

        const filaTexto =
            (fila.dataset.descripcion || '').toLowerCase();

        const filaCodigo =
            (fila.dataset.codigo || '').toLowerCase();

        const coincideFamilia =
            !familia || filaFamilia.includes(familia);

        const coincideBusqueda =
            !busqueda ||
            filaTexto.includes(busqueda) ||
            filaCodigo.includes(busqueda);

        fila.style.display =
            (coincideFamilia && coincideBusqueda)
            ? ''
            : 'none';

    });
}
// =====================================================
// CÁLCULO AUTOMÁTICO DE MARGEN - NUEVO Y EDITAR
// =====================================================

function inicializarCalculoMargen() {

    // === MODAL NUEVO PRODUCTO ===
    const costoNuevo = document.getElementById('costo_unitario');
    const precioNuevo = document.getElementById('precio_unitario');
    const margenNuevo = document.getElementById('margen');

    if (costoNuevo && precioNuevo && margenNuevo) {
        function calcularNuevo() {
            const costo = parseFloat(costoNuevo.value) || 0;
            const precio = parseFloat(precioNuevo.value) || 0;

            if (costo > 0) {
                const margen = ((precio - costo) / costo) * 100;
                margenNuevo.value = margen.toFixed(2);
            } else {
                margenNuevo.value = '';
            }
        }

        costoNuevo.addEventListener('input', calcularNuevo);
        precioNuevo.addEventListener('input', calcularNuevo);
    }

    // === MODAL EDITAR PRODUCTO ===
    const costoEdit = document.getElementById('edit_costo_unitario');
    const precioEdit = document.getElementById('edit_precio_unitario');
    const margenEdit = document.getElementById('edit_margen');

    if (costoEdit && precioEdit && margenEdit) {
        function calcularEdit() {
            const costo = parseFloat(costoEdit.value) || 0;
            const precio = parseFloat(precioEdit.value) || 0;

            if (costo > 0) {
                const margen = ((precio - costo) / costo) * 100;
                margenEdit.value = margen.toFixed(2);
            } else {
                margenEdit.value = '';
            }
        }

        costoEdit.addEventListener('input', calcularEdit);
        precioEdit.addEventListener('input', calcularEdit);
    }
}

// =====================================================
// EJECUTAR AL CARGAR Y AL ABRIR MODALES
// =====================================================
document.addEventListener('DOMContentLoaded', () => {
    inicializarCalculoMargen();

    // Re-inicializar cuando se abra el modal de Nuevo (importante)
    const modalNuevo = document.getElementById('modalNuevoProducto');
    if (modalNuevo) {
        modalNuevo.addEventListener('shown.bs.modal', () => {
            inicializarCalculoMargen();
        });
    }

    // También para el modal de Editar
    const modalEditar = document.getElementById('modalEditarProducto');
    if (modalEditar) {
        modalEditar.addEventListener('shown.bs.modal', () => {
            inicializarCalculoMargen();
        });
    }
});


/* IMPORTAR EXCEL */
document
    .getElementById('btnImportar')
    .addEventListener('click', () => {

        document
            .getElementById('fileInput')
            .click();

    });

document
    .getElementById('fileInput')
    .addEventListener('change', function () {

        if (this.files.length > 0) {

            this.closest('form').submit();

        }

    });

// AGREGAR EN gestion_productos.js

/* SELECT2 */
$(document).ready(function () {


$('#familia').select2({
    dropdownParent: $('#modalNuevoProducto'),
    placeholder: "Buscar familia..."
});

$('#marca').select2({
    dropdownParent: $('#modalNuevoProducto'),
    placeholder: "Buscar marca..."
});

$('#unidad').select2({
    dropdownParent: $('#modalNuevoProducto'),
    placeholder: "Buscar unidad..."
});


});

/* CAMBIO PESO */
document.getElementById('tipo_peso')
.addEventListener('change', function () {

    const rango =
        document.getElementById('contenedor-rango');

    const exacto =
        document.getElementById('contenedor-exacto');

    if (this.value === 'exacto') {

        rango.style.display = 'none';
        exacto.style.display = 'block';

    } else {

        rango.style.display = 'block';
        exacto.style.display = 'none';

    }

});

// =====================================================
// MODALES - EDITAR Y ELIMINAR PRODUCTO
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

    console.log("✅ gestion_productos.js cargado");

    // TBODY DE LA TABLA
    const tbody = document.getElementById('tbody-productos');

    if (!tbody) {
        console.error("❌ No existe tbody-productos");
        return;
    }

    console.log("✅ tbody encontrado");

    // =====================================================
    // DELEGACIÓN DE EVENTOS
    // =====================================================
    tbody.addEventListener('click', function (e) {

        // ================= EDITAR =================
        const btnEditar = e.target.closest('.btn-editar-producto');

        if (btnEditar) {

            console.log("✏️ CLICK EDITAR");

            editarProducto(btnEditar);
            return;
        }

        // ================= ELIMINAR =================
        const btnEliminar = e.target.closest('.btn-eliminar-producto');

        if (btnEliminar) {

            console.log("🗑️ CLICK ELIMINAR");

            eliminarProducto(btnEliminar);
            return;
        }

    });

    // =====================================================
    // BOTÓN GUARDAR EDICIÓN
    // =====================================================
    const btnGuardar = document.getElementById('btnGuardarEdicionProducto');

    if (btnGuardar) {
        btnGuardar.addEventListener('click', guardarEdicionProducto);
    }

});

// =====================================================
// EDITAR PRODUCTO
// =====================================================
function editarProducto(btn) {

    console.log("✏️ EDITAR PRODUCTO");

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

    // RECORRER CAMPOS
    for (const id in campos) {

        const elemento =
            document.getElementById(id);

        if (!elemento) {

            console.error(`❌ NO EXISTE EL ID: ${id}`);
            continue;
        }

        elemento.value =
            campos[id] || '';
    }

    // ABRIR MODAL
    const modal = new bootstrap.Modal(
        document.getElementById('modalEditarProducto')
    );

    modal.show();
}

// =====================================================
// GUARDAR EDICIÓN
// =====================================================
async function guardarEdicionProducto() {

    const id = document.getElementById('edit_id').value;

    if (!id) {
        alert("❌ No se encontró el ID");
        return;
    }

    const datos = {

        familia:
            document.getElementById('edit_familia').value,

        marca:
            document.getElementById('edit_marca').value,

        descripcion:
            document.getElementById('edit_descripcion').value,

        modelo:
            document.getElementById('edit_modelo').value,

        unidad:
            document.getElementById('edit_unidad').value,

        volumen:
            document.getElementById('edit_volumen').value,

        transporte:
            document.getElementById('edit_transporte').value,

        observaciones:
            document.getElementById('edit_observaciones').value,

        descripcion_larga:
            document.getElementById('edit_descripcion_larga').value,

        costo_unitario:
            parseFloat(document.getElementById('edit_costo_unitario').value) || 0,

        precio_unitario:
            parseFloat(document.getElementById('edit_precio_unitario').value) || 0,

        stock:
            parseInt(document.getElementById('edit_stock').value) || 0
    };

    try {

        const response = await fetch(`/api/productos/${id}`, {

            method: 'PUT',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify(datos)

        });

        if (response.ok) {

            alert("✅ Producto actualizado");

            // CERRAR MODAL
            bootstrap.Modal.getInstance(
                document.getElementById('modalEditarProducto')
            ).hide();

            // RECARGAR TABLA
            if (typeof cargarProductos === "function") {
                cargarProductos();
            }

        } else {

            alert("❌ Error al actualizar");

        }

    } catch (error) {

        console.error(error);

        alert("❌ Error de conexión");

    }

}

// =====================================================
// ELIMINAR PRODUCTO
// =====================================================
function eliminarProducto(btn) {

    const id =
        btn.dataset.id;

    const descripcion =
        btn.dataset.descripcion || 'Producto';

    document.getElementById('eliminar_id_producto').value =
        id;

    document.getElementById('textoProductoEliminar').textContent =
        descripcion;

    // ABRIR MODAL
    const modal = new bootstrap.Modal(
        document.getElementById('modalEliminarProducto')
    );

    modal.show();
}
