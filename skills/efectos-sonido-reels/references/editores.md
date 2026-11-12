# Montaje del mapa en Premiere Pro y DaVinci Resolve

Usa esto para escribir la sección "Montaje" del mapa. Elige solo el editor de la persona y da 4 a 6 pasos concretos, no todo.

## Pistas (los dos editores)
Una pista por familia hace que la mezcla sea rápida: subes o bajas todos los whooshes de una vez.
- A1 Voz · A2 Música · A3 Transiciones · A4 Texto/UI · A5 Impactos · A6 Foley · A7 Ambiente

Ponle nombre a cada pista. En los desgloses profesionales se ven 10 o más pistas de SFX en un reel de 15 segundos, y eso es normal.

## Premiere Pro
- **Traer los sonidos**: la extensión de Envato (Ventana > Extensiones > Envato) busca, previsualiza e importa sin salir de Premiere. Pega ahí los términos del mapa. Si no la tienen, se instala desde Adobe Exchange (Creative Cloud > Plugins > buscar "Envato").
- **Ir a un timecode**: haz clic en el timecode azul de la línea de tiempo, escribe el número (por ejemplo `00:00:07:15`) y pulsa Enter. Pon un marcador con `M` en cada momento del mapa antes de arrastrar sonidos.
- **Volumen**: selecciona el clip, abre Controles de efectos > Volumen > Nivel, o usa Ganancia de audio (`G`). Mira los vúmetros: la voz con picos cerca de −6 dB y nada por encima de −1 dB en la mezcla.
- **Ducking**: en el panel Sonido esencial, marca la voz como *Diálogo*, la música como *Música* y los efectos como *SFX*. En la música activa *Atenuación* (ducking) contra Diálogo para que baje sola cuando hay voz.
- **Fundidos**: aplica *Fundido exponencial* de 3 a 6 fotogramas en las colas largas y en el ambiente. Los whooshes y hits normalmente no necesitan fundido de entrada.

## DaVinci Resolve
- **Timecode +1 hora**: la línea de tiempo suele empezar en `01:00:00:00`, así que `00:00:07:15` del mapa es `01:00:07:15` en DaVinci. Haz clic en el timecode sobre el visor, escribe el número y pulsa Enter. Pon un marcador con `M` en cada momento.
- **Traer los sonidos**: descárgalos desde la web de Envato y arrástralos al Media Pool, mejor en una carpeta "SFX" por familias para reutilizarlos.
- **Volumen**: en la página Edit, selecciona el clip, abre Inspector > Audio > Volume. En la página Fairlight ajustas toda la pista con su fader. Misma regla: voz con picos cerca de −6 dB y nada por encima de −1 dB.
- **Ducking**: baja la música bajo la voz con keyframes de volumen, o con el compresor de Fairlight (Dynamics) en la pista de música usando la voz como sidechain.
- **Fundidos**: arrastra las manijas de fundido en la esquina del clip, de 3 a 6 fotogramas en colas y ambiente.

## Comprobación final (los dos)
1. Escucha el reel completo con audífonos y luego con el altavoz del celular. Ahí se escuchan la mayoría de los reels, y los graves (sub drops) casi desaparecen. Si el impacto depende solo del grave, súmale una capa con más medios.
2. Revisa que ninguna palabra clave quede tapada.
3. Si algo suena repetido, cambia la variante del whoosh o del pop.
