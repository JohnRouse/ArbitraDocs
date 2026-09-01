using System.Collections.ObjectModel;
using ArbitraDocs.WinUI.Models;
using ArbitraDocs.WinUI.Services;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;
using Windows.Storage.Pickers;

namespace ArbitraDocs.WinUI.Pages;

public sealed partial class MergeFolioPage : Page
{
    public ObservableCollection<PdfFileItem> Files { get; } = new();
    private readonly EngineService _engine = new();

    public MergeFolioPage()
    {
        InitializeComponent();
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

        var options = new DocumentProcessOptions(
            NormalizeA4: NormalizeToggle.IsOn,
            PreserveExistingA4: PreserveA4Toggle.IsOn,
            PageMarginMm: SafeValue(PageMarginBox, 8),
            EnlargeSmallPages: EnlargeSmallToggle.IsOn,
            Foliate: FoliateToggle.IsOn,
            StartNumber: (int)Math.Round(SafeValue(StartNumberBox, 1)),
            Direction: SelectedTag(DirectionCombo, "asc"),
            Mode: SelectedTag(ModeCombo, "numero+letras"),
            Position: SelectedTag(PositionCombo, "top-right"),
            FontSize: SafeValue(FontSizeBox, 8),
            FolioMarginXmm: SafeValue(FolioMarginXBox, 10),
            FolioMarginYmm: SafeValue(FolioMarginYBox, 6));

        SetBusy(true);
        try
        {
            await _engine.ProcessAsync(
                Files.Select(x => x.Path).ToList(),
                output.Path,
                options);

            ShowStatus($"PDF generado correctamente: {output.Name}", InfoBarSeverity.Success);
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

    private void AddFile(string path)
    {
        if (Files.Any(x => string.Equals(x.Path, path, StringComparison.OrdinalIgnoreCase)))
        {
            return;
        }

        Files.Add(new PdfFileItem
        {
            Name = System.IO.Path.GetFileName(path),
            Path = path,
        });
    }

    private static double SafeValue(NumberBox box, double fallback)
        => double.IsNaN(box.Value) ? fallback : box.Value;

    private static string SelectedTag(ComboBox combo, string fallback)
        => (combo.SelectedItem as ComboBoxItem)?.Tag?.ToString() ?? fallback;

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
}
