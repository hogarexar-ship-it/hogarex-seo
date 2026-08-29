export default async function handler(req, res) {
  try {
    const response = await fetch(
      "https://hogarex.ar/api/1.1/obj/trader"
    );

    if (!response.ok) {
      return res.status(response.status).json({
        error: "Error al consultar Bubble"
      });
    }

    const data = await response.json();

    return res.status(200).json(data);

  } catch (error) {
    return res.status(500).json({
      error: "No se pudo conectar con Bubble"
    });
  }
}
