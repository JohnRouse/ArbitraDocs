using System.Collections.ObjectModel;
using ArbitraDocs.WinUI.Models;
using ArbitraDocs.WinUI.Services;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;
using Windows.Storage.Pickers;
using Windows.UI.Text;

namespace ArbitraDocs.WinUI.Pages;

public sealed partial class MergeFolioPage : Page
{
    public ObservableCollection<PdfFileItem> Files { get; } = new();
    private readonly EngineService _engine = new();
    private string? _certificatePath;

    public MergeFolioPage()
    {
        InitializeComponent();
    }

    private void Page_Loaded(object sender, RoutedEventArgs e)
    {
        UpdatePreview();
    }

    private async void AddPdf_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FileOpenPicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
            ViewMode = PickerViewMode.List,
        };
        picker.FileTypeFilter.Add(".pdf");
        InitializePicker(picker);

        var selected = await picker.PickMultipleFilesAsync();
        foreach (var file in selected)
        {
            AddFile(file.Path);
        }
    }

    private async void SelectCertificate_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FileOpenPicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
            ViewMode = PickerViewMode.List,
        };
        picker.FileTypeFilter.Add(".pdf");
        InitializePicker(picker);

        var selected = await picker.PickSingleFileAsync();
        if (selected is null)
        {
            return;
        }

        _certificatePath = selected.Path;
        CertificateFileText.Text = selected.Name;
    }

    private void RemovePdf_Click(object sender, RoutedEventArgs e)
    {
        if (PdfList.SelectedItem is PdfFileItem selected)
        {
            Files.Remove(selected);
        }
    }

    private void MoveUp_Click(object sender, RoutedEventArgs e)
    {
        if (PdfList.SelectedItem is not PdfFileItem selected)
        {
            return;
        }

        var index = Files.IndexOf(selected);
        if (index > 0)
        {
            Files.Move(index, index - 1);
            PdfList.SelectedItem = selected;
        }
    }

    private void MoveDown_Click(object sender, RoutedEventArgs e)
    {
        if (PdfList.SelectedItem is not PdfFileItem selected)
        {
            return;
        }

        var index = Files.IndexOf(selected);
        if (index >= 0 && index < Files.Count - 1)
        {
            Files.Move(index, index + 1);
            PdfList.SelectedItem = selected;
        }
    }

    private void Clear_Click(object sender, RoutedEventArgs e)
    {
        Files.Clear();
    }

    private void DropZone_DragOver(object sender, DragEventArgs e)
    {
        if (e.DataView.Contains(StandardDataFormats.StorageItems))
        {
            e.AcceptedOperation = DataPackageOperation.Copy;
            e.DragUIOverride.Caption = "Agregar PDF a ArbitraDocs";
            e.DragUIOverride.IsCaptionVisible = true;
        }
    }

    private async void DropZone_Drop(object sender, DragEventArgs e)
    {
        if (!e.DataView.Contains(StandardDataFormats.StorageItems))
        {
            return;
        }

        var items = await e.DataView.GetStorageItemsAsync();
        foreach (var file in items.OfType<StorageFile>())
        {
            if (string.Equals(file.FileType, ".pdf", StringComparison.OrdinalIgnoreCase))
            {
                AddFile(file.Path);
            }
        }
    }

    private async void ProcessButton_Click(object sender, RoutedEventArgs e)
    {
        StatusBar.IsOpen = false;

        if (Files.Count == 0)
        {
            ShowStatus("Agrega al menos un PDF.", InfoBarSeverity.Warning);
            return;
        }

        if (CertifyToggle.IsOn && (string.IsNullOrWhiteSpace(_certificatePath) || !File.Exists(_certificatePath)))
        {
            ShowStatus("Activa la certificación solo después de seleccionar el PDF de certificación.", InfoBarSeverity.Warning);
            return;
        }

        var options = BuildOptions();
        var outputMode = SelectedTag(OutputModeCombo, "joined");

        SetBusy(true);
        try
        {
            if (outputMode == "separate")
            {
                await ProcessSeparateAsync(options);
            }
            else
            {
                await ProcessJoinedAsync(options);
            }
        }
        catch (Exception ex)
        {
            ShowStatus(ex.Message, InfoBarSeverity.Error);
        }
        finally
        {
            SetBusy(false);
        }
    }

    private async Task ProcessJoinedAsync(DocumentProcessOptions options)
    {
        var savePicker = new FileSavePicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
            SuggestedFileName = "ArbitraDocs_resultado",
        };
        savePicker.FileTypeChoices.Add("Documento PDF", new List<string> { ".pdf" });
        InitializePicker(savePicker);

        var output = await savePicker.PickSaveFileAsync();
        if (output is null)
        {
            return;
        }

        await _engine.ProcessAsync(
            Files.Select(x => x.Path).ToList(),
            output.Path,
            options);

        ShowStatus($"PDF generado correctamente: {output.Name}", InfoBarSeverity.Success);
    }

    private async Task ProcessSeparateAsync(DocumentProcessOptions options)
    {
        var picker = new FolderPicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
        };
        picker.FileTypeFilter.Add("*");
        InitializePicker(picker);

        var folder = await picker.PickSingleFolderAsync();
        if (folder is null)
        {
            return;
        }

        var generated = 0;
        foreach (var item in Files)
        {
            var baseName = Path.GetFileNameWithoutExtension(item.Name) + "_ArbitraDocs.pdf";
            var outputPath = UniqueOutputPath(folder.Path, baseName);
            await _engine.ProcessAsync(new[] { item.Path }, outputPath, options);
            generated++;
        }

        ShowStatus($"Se generaron {generated} PDF separados en {folder.Name}.", InfoBarSeverity.Success);
    }

    private DocumentProcessOptions BuildOptions()
    {
        return new DocumentProcessOptions(
            NormalizeA4: NormalizeToggle.IsOn,
            PreserveExistingA4: PreserveA4Toggle.IsOn,
            PageMarginMm: SafeValue(PageMarginBox, 8),
            EnlargeSmallPages: EnlargeSmallToggle.IsOn,
            Foliate: FoliateToggle.IsOn,
            StartNumber: (int)Math.Round(SafeValue(StartNumberBox, 1)),
            Direction: SelectedTag(DirectionCombo, "asc"),
            Mode: SelectedTag(ModeCombo, "numero+letras"),
            Position: SelectedTag(PositionCombo, "top-right"),
            FontFamily: SelectedTag(FontFamilyCombo, "Arial"),
            Bold: BoldButton.IsChecked == true,
            Italic: ItalicButton.IsChecked == true,
            FontSize: SafeValue(FontSizeBox, 8),
            FolioMarginXmm: SafeValue(FolioMarginXBox, 10),
            FolioMarginYmm: SafeValue(FolioMarginYBox, 6),
            Certify: CertifyToggle.IsOn,
            CertificatePdf: _certificatePath);
    }

    private void PreviewSelection_Changed(object sender, SelectionChangedEventArgs e)
    {
        UpdatePreview();
    }

    private void PreviewNumber_ValueChanged(NumberBox sender, NumberBoxValueChangedEventArgs args)
    {
        UpdatePreview();
    }

    private void PreviewToggle_Changed(object sender, RoutedEventArgs e)
    {
        UpdatePreview();
    }

    private void UpdatePreview()
    {
        if (PreviewFolioText is null || ModeCombo is null || PositionCombo is null || FontFamilyCombo is null)
        {
            return;
        }

        var number = Math.Clamp((int)Math.Round(SafeValue(StartNumberBox, 1)), 0, 999_999_999);
        var words = NumberToSpanish(number).ToUpperInvariant();
        var mode = SelectedTag(ModeCombo, "numero+letras");
        PreviewFolioText.Text = mode switch
        {
            "numero" => number.ToString(),
            "letras" => words,
            _ => $"{number}\n{words}",
        };

        var family = SelectedTag(FontFamilyCombo, "Arial");
        PreviewFolioText.FontFamily = new FontFamily(family);
        PreviewFolioText.FontWeight = BoldButton?.IsChecked == true ? FontWeights.Bold : FontWeights.Normal;
        PreviewFolioText.FontStyle = ItalicButton?.IsChecked == true ? FontStyle.Italic : FontStyle.Normal;
        PreviewFolioText.FontSize = Math.Clamp(SafeValue(FontSizeBox, 8) * 1.05, 8, 28);
        PreviewFolioText.Opacity = FoliateToggle?.IsOn == true ? 1.0 : 0.22;

        var position = SelectedTag(PositionCombo, "top-right");
        PreviewFolioText.HorizontalAlignment = position.EndsWith("left", StringComparison.Ordinal)
            ? HorizontalAlignment.Left
            : position.EndsWith("center", StringComparison.Ordinal)
                ? HorizontalAlignment.Center
                : HorizontalAlignment.Right;
        PreviewFolioText.VerticalAlignment = position.StartsWith("bottom", StringComparison.Ordinal)
            ? VerticalAlignment.Bottom
            : VerticalAlignment.Top;
        PreviewFolioText.TextAlignment = position.EndsWith("left", StringComparison.Ordinal)
            ? TextAlignment.Left
            : position.EndsWith("center", StringComparison.Ordinal)
                ? TextAlignment.Center
                : TextAlignment.Right;

        var marginX = Math.Clamp(SafeValue(FolioMarginXBox, 10) * 1.2, 0, 72);
        var marginY = Math.Clamp(SafeValue(FolioMarginYBox, 6) * 1.2, 0, 72);
        PreviewFolioText.Margin = position switch
        {
            "top-left" => new Thickness(marginX, marginY, 0, 0),
            "top-center" => new Thickness(0, marginY, 0, 0),
            "top-right" => new Thickness(0, marginY, marginX, 0),
            "bottom-left" => new Thickness(marginX, 0, 0, marginY),
            "bottom-center" => new Thickness(0, 0, 0, marginY),
            _ => new Thickness(0, 0, marginX, marginY),
        };
    }

    private void AddFile(string path)
    {
        if (Files.Any(x => string.Equals(x.Path, path, StringComparison.OrdinalIgnoreCase)))
        {
            return;
        }

        Files.Add(new PdfFileItem
        {
            Name = Path.GetFileName(path),
            Path = path,
        });
    }

    private static string UniqueOutputPath(string folder, string fileName)
    {
        var candidate = Path.Combine(folder, fileName);
        if (!File.Exists(candidate))
        {
            return candidate;
        }

        var stem = Path.GetFileNameWithoutExtension(fileName);
        var extension = Path.GetExtension(fileName);
        var index = 2;
        do
        {
            candidate = Path.Combine(folder, $"{stem} ({index}){extension}");
            index++;
        }
        while (File.Exists(candidate));

        return candidate;
    }

    private static double SafeValue(NumberBox box, double fallback)
        => box is null || double.IsNaN(box.Value) ? fallback : box.Value;

    private static string SelectedTag(ComboBox combo, string fallback)
        => (combo?.SelectedItem as ComboBoxItem)?.Tag?.ToString() ?? fallback;

    private static void InitializePicker(object picker)
    {
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
        WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
    }

    private void SetBusy(bool busy)
    {
        ProcessButton.IsEnabled = !busy;
        ProcessingRing.IsActive = busy;
        ProcessingRing.Visibility = busy ? Visibility.Visible : Visibility.Collapsed;
    }

    private void ShowStatus(string message, InfoBarSeverity severity)
    {
        StatusBar.Message = message;
        StatusBar.Severity = severity;
        StatusBar.IsOpen = true;
    }

    private static string NumberToSpanish(int number)
    {
        if (number < 30)
        {
            string[] units =
            {
                "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
                "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho",
                "diecinueve", "veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco",
                "veintiséis", "veintisiete", "veintiocho", "veintinueve",
            };
            return units[number];
        }

        if (number < 100)
        {
            var tens = (number / 10) * 10;
            var unit = number % 10;
            var tensText = tens switch
            {
                30 => "treinta",
                40 => "cuarenta",
                50 => "cincuenta",
                60 => "sesenta",
                70 => "setenta",
                80 => "ochenta",
                _ => "noventa",
            };
            return unit == 0 ? tensText : $"{tensText} y {NumberToSpanish(unit)}";
        }

        if (number < 1000)
        {
            if (number == 100)
            {
                return "cien";
            }
            if (number < 200)
            {
                return $"ciento {NumberToSpanish(number - 100)}";
            }

            var hundreds = (number / 100) * 100;
            var rest = number % 100;
            var hundredText = hundreds switch
            {
                200 => "doscientos",
                300 => "trescientos",
                400 => "cuatrocientos",
                500 => "quinientos",
                600 => "seiscientos",
                700 => "setecientos",
                800 => "ochocientos",
                _ => "novecientos",
            };
            return rest == 0 ? hundredText : $"{hundredText} {NumberToSpanish(rest)}";
        }

        var millions = number / 1_000_000;
        var remainder = number % 1_000_000;
        var parts = new List<string>();

        if (millions > 0)
        {
            parts.Add(millions == 1
                ? "un millón"
                : $"{ApocopateOne(NumberToSpanish(millions))} millones");
        }

        var thousands = remainder / 1000;
        var unitsPart = remainder % 1000;
        if (thousands > 0)
        {
            parts.Add(thousands == 1
                ? "mil"
                : $"{ApocopateOne(NumberToSpanish(thousands))} mil");
        }

        if (unitsPart > 0)
        {
            parts.Add(NumberToSpanish(unitsPart));
        }

        return string.Join(" ", parts);
    }

    private static string ApocopateOne(string text)
    {
        if (text.EndsWith("veintiuno", StringComparison.Ordinal))
        {
            return text[..^9] + "veintiún";
        }
        if (text.EndsWith(" y uno", StringComparison.Ordinal))
        {
            return text[..^5] + " y un";
        }
        if (text.EndsWith("uno", StringComparison.Ordinal))
        {
            return text[..^3] + "un";
        }
        return text;
    }
}
