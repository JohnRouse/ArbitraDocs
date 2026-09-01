using System.Collections.ObjectModel;
using ArbitraDocs.WinUI.Models;
using Microsoft.UI.Xaml.Controls;

namespace ArbitraDocs.WinUI.Pages;

public sealed partial class HomePage : Page
{
    public ObservableCollection<ToolCardItem> Tools { get; } = new()
    {
        new() { Key = "mergefolio", Name = "Unir y foliar PDF", Description = "Une varios PDFs, normaliza a A4 y agrega foliación configurable.", Available = true },
        new() { Key = "compress", Name = "Comprimir PDF", Description = "Reducir el peso de un documento PDF.", Available = false },
        new() { Key = "ocr", Name = "OCR en PDF", Description = "Reconocer texto dentro de PDFs escaneados.", Available = false },
        new() { Key = "split", Name = "Dividir PDF", Description = "Separar páginas o rangos en nuevos documentos.", Available = false },
        new() { Key = "rotate", Name = "Girar PDF", Description = "Rotar páginas seleccionadas o todo el documento.", Available = false },
        new() { Key = "pdf-images", Name = "PDF a imágenes", Description = "Convertir páginas a JPG, PNG o WEBP.", Available = false },
        new() { Key = "office-pdf", Name = "Office a PDF", Description = "Convertir Word, Excel y PowerPoint a PDF.", Available = false },
        new() { Key = "images-pdf", Name = "Imágenes a PDF", Description = "Crear PDF desde JPG, PNG o WEBP.", Available = false },
        new() { Key = "protect", Name = "Proteger PDF", Description = "Agregar contraseña y restricciones al PDF.", Available = false },
        new() { Key = "watermark", Name = "Marca de agua", Description = "Agregar texto o imagen como marca de agua.", Available = false },
        new() { Key = "certify", Name = "Certificar PDF", Description = "Intercalar certificación al reverso de cada página.", Available = false },
        new() { Key = "normalize-names", Name = "Normalizar nombres", Description = "Corregir nombres y rutas problemáticas para Windows y OneDrive.", Available = false },
    };

    public HomePage()
    {
        InitializeComponent();
    }

    private void ToolGrid_ItemClick(object sender, ItemClickEventArgs e)
    {
        if (e.ClickedItem is not ToolCardItem tool || !tool.Available)
        {
            return;
        }

        if (tool.Key == "mergefolio")
        {
            App.MainWindow.NavigateToMergeFolio();
        }
    }
}
