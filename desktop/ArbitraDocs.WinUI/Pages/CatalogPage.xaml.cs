using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace ArbitraDocs.WinUI.Pages;

public sealed partial class CatalogPage : Page
{
    public CatalogPage()
    {
        InitializeComponent();
    }

    protected override void OnNavigatedTo(NavigationEventArgs e)
    {
        base.OnNavigatedTo(e);
        var key = e.Parameter?.ToString() ?? "pdf";
        (TitleText.Text, DescriptionText.Text) = key switch
        {
            "convert" => ("Conversiones", "PDF a JPG, PNG, WEBP, Word, Excel y PowerPoint; Word, Excel, PowerPoint e imágenes a PDF."),
            "special" => ("Herramientas especiales", "Foliar PDF, Certificar PDF y Normalizar nombres y rutas."),
            _ => ("Herramientas PDF", "Unir, comprimir, OCR, dividir, girar, aplanar, proteger, desbloquear, firmar, marca de agua y recortar PDF."),
        };
    }
}
