// static/js/productos.js

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
// MODAL EDITAR PRODUCTO
// =====================================================

document.querySelectorAll('.btn-editar-producto')
    .forEach(btn => {

        btn.addEventListener('click', function () {

            // ID
            document.getElementById('edit_id').value =
                this.dataset.id || '';

            // FAMILIA
            document.getElementById('edit_familia').value =
                this.dataset.familia || '';

            // DESCRIPCION
            document.getElementById('edit_descripcion').value =
                this.dataset.descripcion || '';

            // DESCRIPCION LARGA
            document.getElementById('edit_descripcion_larga').value =
                this.dataset.descripcion_larga || '';

            // MARCA
            document.getElementById('edit_marca').value =
                this.dataset.marca || '';

            // MODELO
            document.getElementById('edit_modelo').value =
                this.dataset.modelo || '';

            // UNIDAD
            document.getElementById('edit_unidad').value =
                this.dataset.unidad || '';

            // PESO
            document.getElementById('edit_peso').value =
                this.dataset.peso || '';

            // VOLUMEN
            document.getElementById('edit_volumen').value =
                this.dataset.volumen || '';

            // OBSERVACIONES
            document.getElementById('edit_observaciones').value =
                this.dataset.observaciones || '';

            // TRANSPORTE
            document.getElementById('edit_transporte').value =
                this.dataset.transporte || '';

            // ABRIR MODAL
            const modalEditar =
                new bootstrap.Modal(
                    document.getElementById(
                        'modalEditarProducto'
                    )
                );

            modalEditar.show();

        });

    });



// =====================================================
// MODAL ELIMINAR PRODUCTO
// =====================================================

document.querySelectorAll('.btn-eliminar-producto')
    .forEach(btn => {

        btn.addEventListener('click', function () {

            const id =
                this.dataset.id;

            const descripcion =
                this.dataset.descripcion;

            // INPUT HIDDEN
            document.getElementById(
                'eliminar_id_producto'
            ).value = id;

            // TEXTO PRODUCTO
            document.getElementById(
                'textoProductoEliminar'
            ).textContent = descripcion;

            // ABRIR MODAL
            const modalEliminar =
                new bootstrap.Modal(
                    document.getElementById(
                        'modalEliminarProducto'
                    )
                );

            modalEliminar.show();

        });

    });
