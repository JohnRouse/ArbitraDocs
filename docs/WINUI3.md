# Interfaz WinUI 3

ArbitraDocs adopta **WinUI 3 + C# + Windows App SDK** como interfaz de escritorio definitiva.

## Objetivo

Evitar una apariencia de aplicación clásica y ofrecer una experiencia coherente con Windows 11: Fluent Design, navegación lateral, Mica cuando esté disponible, tarjetas, controles modernos, tema claro/oscuro y drag & drop.

## Arquitectura

La aplicación se divide en dos procesos locales:

```text
ArbitraDocs.exe                 WinUI 3 / C#
        │
        └── Engine/ArbitraDocs.Engine.exe
                    │
                    └── motor documental actual
```

El motor se ejecuta únicamente en la misma computadora. No se suben documentos a servidores externos.

Esta separación permite evolucionar la interfaz sin acoplarla a las bibliotecas PDF/OCR/conversión y facilita incorporar motores especializados en el futuro.

## Beta inicial

La primera pantalla funcional conecta WinUI 3 con el flujo:

1. agregar múltiples PDFs;
2. reordenarlos, incluido drag & drop;
3. unir;
4. normalizar opcionalmente a A4;
5. conservar A4 existente al 100 % o aplicar margen también sobre A4;
6. ampliar opcionalmente páginas pequeñas;
7. foliar opcionalmente;
8. elegir inicio, dirección, formato y posición;
9. configurar tamaño y márgenes horizontal/vertical del folio;
10. guardar el PDF final.

## Distribución de la beta

El build de pruebas es autocontenido. El usuario no necesita instalar Python ni .NET/Windows App SDK manualmente.

Durante desarrollo se distribuye como carpeta portable comprimida. La distribución pública se envolverá en `ArbitraDocs_Setup.exe`, de modo que el usuario solo instale y abra ArbitraDocs.

## Windows App SDK

La interfaz usa Windows App SDK 2.4.0 y se publica como aplicación WinUI 3 desempaquetada y autocontenida para simplificar las pruebas en PCs comunes.
