# Trajes "New Style" de Pyra y Mythra para XC2 (Switch 1)

Mod para Xenoblade Chronicles 2 v3.0.1 de Switch 1: lleva los trajes New Style de Pyra y Mythra,
con el arte del menú. **Repositorio privado, de uso personal**: los modelos y artes pertenecen a
Nintendo / Monolith Soft y no deben redistribuirse.

## Descargar (sección Releases, v1.0)

| Zip | Para | Instalación | Probado |
|---|---|---|---|
| `...-PC.zip` | Port de PC (xc2-recomp) | descomprimir dentro de `mods/` | sí |
| `...-consola-DLC.zip` | Atmosphère, con el DLC | raíz de la microSD | no |
| `...-consola-sin-DLC.zip` | Atmosphère, sin DLC (plugin xcnx-file-loader de RoccoDev) | raíz de la microSD | no |

Instalá uno solo, quitá antes las versiones viejas del mod y hacé copia de la partida.

## Contenido de la v1.0
- Modelos: Pyra v19 (`bl000101`), Mythra v28 (`bl000201`).
- Arte y brillo del menú: `fim_bl_001/002` y `fim_bl_glow_001/002`.

## Diferencias con Switch 2
Los shaders de Switch 2 no corren en Switch 1, así que se usan materiales de Switch 1.
La galaxia es estática y la pollera de Mythra no tiene el velo translúcido.

## scripts/
Historial de los scripts de construcción (Blender 5.2 + addon `xenoblade_blender`). Los finales son
`bl_build_v19.py` + `post_v19.py` (Pyra) y `bl_build_mythra_v16.py` + `postM3.py` +
`tex_mythra_piernas_v28.py` (Mythra). Tienen rutas locales y no incluyen archivos del juego.
