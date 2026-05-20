// =========================
// NUEVO PROVEEDOR ERP
// =========================
console.log("🔥 nuevo_proveedor.js cargado");
document.addEventListener('DOMContentLoaded', function () {

    // =====================================================
    // SELECT2
    // =====================================================

    if (typeof $ !== 'undefined' && $('#condicion_pago').length) {

        $('#condicion_pago').select2({
            placeholder: "Buscar condición de pago...",
            allowClear: true,
            width: '100%',
            dropdownParent: $('#modalNuevoProveedor')
        });

    }

    // =====================================================
    // CONDICIÓN DE PAGO
    // =====================================================

    const condicionPago =
        document.getElementById('condicion_pago');

    const campoTiempoCredito =
        document.getElementById('campo_tiempo_credito');

    if (condicionPago) {

        condicionPago.addEventListener('change', function () {

            if (this.value === 'Credito') {

                campoTiempoCredito.style.display = 'block';

            } else {

                campoTiempoCredito.style.display = 'none';

                const tiempoCredito =
                    document.getElementById('tiempo_credito');

                if (tiempoCredito) {
                    tiempoCredito.value = '';
                }

            }

        });

    }

    // =====================================================
    // DISTRITOS
    // =====================================================

    const distritos = [

        "Ancón",
        "Ate",
        "Barranco",
        "Breña",
        "Carabayllo",
        "Chaclacayo",
        "Chorrillos",
        "Cieneguilla",
        "Comas",
        "El Agustino",
        "Independencia",
        "Jesús María",
        "La Molina",
        "La Victoria",
        "Lince",
        "Los Olivos",
        "Lurigancho",
        "Lurín",
        "Magdalena del Mar",
        "Miraflores",
        "Pachacámac",
        "Pucusana",
        "Pueblo Libre",
        "Puente Piedra",
        "Punta Hermosa",
        "Punta Negra",
        "Rímac",
        "San Bartolo",
        "San Borja",
        "San Isidro",
        "San Juan de Lurigancho",
        "San Juan de Miraflores",
        "San Luis",
        "San Martín de Porres",
        "San Miguel",
        "Santa Anita",
        "Santa María del Mar",
        "Santa Rosa",
        "Santiago de Surco",
        "Surquillo",
        "Villa El Salvador",
        "Villa María del Triunfo"

    ];

    distritos.sort();

    // =====================================================
    // ELEMENTOS
    // =====================================================

    const tipoRecojo =
        document.getElementById('tipo_recojo');

    const bloqueLista =
        document.getElementById('bloque_lista_distritos');

    const bloqueManual =
        document.getElementById('bloque_manual');

    const buscador =
        document.getElementById('buscarDistrito');

    const select =
        document.getElementById('lugar_recojo');

    // =====================================================
    // CAMBIO TIPO RECOJO
    // =====================================================

    if (tipoRecojo) {

        tipoRecojo.addEventListener('change', function () {

            if (this.value === 'lista') {

                bloqueLista.style.display = 'block';
                bloqueManual.style.display = 'none';

                renderDistritos();

            }

            else if (this.value === 'manual') {

                bloqueLista.style.display = 'none';
                bloqueManual.style.display = 'block';

            }

            else {

                bloqueLista.style.display = 'none';
                bloqueManual.style.display = 'none';

            }

        });

    }

    // =====================================================
    // RENDER DISTRITOS
    // =====================================================

    function renderDistritos(filtro = '') {

        if (!select) return;

        select.innerHTML = '';

        const filtrados = distritos.filter(distrito =>
            distrito.toLowerCase()
                .includes(filtro.toLowerCase())
        );

        if (filtrados.length === 0) {

            const option =
                document.createElement('option');

            option.textContent =
                'No se encontraron resultados';

            option.disabled = true;

            select.appendChild(option);

            return;

        }

        filtrados.forEach(distrito => {

            const option =
                document.createElement('option');

            option.value = distrito;
            option.textContent = distrito;

            select.appendChild(option);

        });

    }

    // =====================================================
    // BUSCADOR DISTRITOS
    // =====================================================

    if (buscador) {

        buscador.addEventListener('focus', function () {

            renderDistritos(this.value);

        });

        buscador.addEventListener('input', function () {

            renderDistritos(this.value);

        });

    }

    // =====================================================
    // SELECCIONAR DISTRITO
    // =====================================================

    if (select) {

        select.addEventListener('change', function () {

            buscador.value = this.value;

        });

    }

    // =====================================================
    // VALIDACIÓN RUC
    // =====================================================

    const rucInput =
        document.getElementById('ruc');

    if (rucInput) {

        rucInput.addEventListener('input', function () {

            this.value =
                this.value.replace(/\D/g, '');

            if (this.value.length > 11) {

                this.value =
                    this.value.slice(0, 11);

            }

        });

    }

    // =====================================================
    // VALIDACIÓN TELÉFONO
    // =====================================================

    const telefonoInput =
        document.getElementById('telefono');

    if (telefonoInput) {

        telefonoInput.addEventListener('input', function () {

            this.value =
                this.value.replace(/[^\d+]/g, '');

        });

    }

});

// ========================================
// GUARDAR PROVEEDOR
// ========================================

const btnGuardarProveedor =
    document.getElementById('btnGuardarProveedor');

if (btnGuardarProveedor) {

    btnGuardarProveedor.addEventListener('click', async function () {

        console.log("🔥 CLICK GUARDAR");

        try {

            let lugarRecojo = '';

            const tipoRecojo =
                document.getElementById('tipo_recojo');

            if (tipoRecojo.value === 'lista') {

                lugarRecojo =
                    document.getElementById('lugar_recojo').value;

            }

            else if (tipoRecojo.value === 'manual') {

                lugarRecojo =
                    document.getElementById('otro_distrito').value;

            }

            const data = {

                razon_social:
                    document.getElementById('razon_social').value,

                razon_comercial:
                    document.getElementById('razon_comercial').value,

                direccion:
                    document.getElementById('direccion').value,

                contacto:
                    document.getElementById('contacto').value,

                ruc:
                    document.getElementById('ruc').value,

                telefono:
                    document.getElementById('telefono').value,

                email:
                    document.getElementById('email').value,

                condicion_pago:
                    document.getElementById('condicion_pago').value,

                tiempo_credito:
                    document.getElementById('tiempo_credito').value,

                banco:
                    document.querySelector('[name="banco"]').value,

                numero_cuenta_cci:
                    document.getElementById('numero_cuenta_cci').value,

                lugar_recojo:
                    lugarRecojo

            };

            console.log(data);

            const response = await fetch('/api/proveedores', {

                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify(data)

            });

            const result = await response.json();

            console.log(result);

            if (result.success) {

                alert('✅ Proveedor guardado');

                location.reload();

            } else {

                alert('❌ Error al guardar');

            }

        } catch (error) {

            console.log(error);

            alert('❌ Error servidor');

        }

    });

}