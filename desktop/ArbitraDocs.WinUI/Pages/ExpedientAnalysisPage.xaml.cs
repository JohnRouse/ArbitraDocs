using System.Collections.ObjectModel;
using System.Diagnostics;
using ArbitraDocs.WinUI.Models;
using ArbitraDocs.WinUI.Services;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;
using Windows.Storage.Pickers;

namespace ArbitraDocs.WinUI.Pages;

public sealed partial class ExpedientAnalysisPage : Page
{
    public ObservableCollection<ContractDetection> Contracts { get; } = new();
    public ObservableCollection<PaymentDetection> Payments { get; } = new();

    private readonly EngineService _engine = new();
    private string? _source;
    private string? _outputDirectory;

    public ExpedientAnalysisPage()
    {
        InitializeComponent();
    }

    private async void SelectFile_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FileOpenPicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
            ViewMode = PickerViewMode.List,
        };
        picker.FileTypeFilter.Add("*");
        InitializePicker(picker);

        var file = await picker.PickSingleFileAsync();
        if (file is null)
        {
            return;
        }

        var extension = file.FileType.ToLowerInvariant();
        if (extension is not ".zip" and not ".rar" and not ".pdf")
        {
            ShowStatus("Selecciona un archivo ZIP, RAR o PDF. También puedes usar el botón Carpeta.", InfoBarSeverity.Warning);
            return;
        }

        SetSource(file.Path);
    }

    private async void SelectFolder_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FolderPicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
        };
        picker.FileTypeFilter.Add("*");
        InitializePicker(picker);

        var folder = await picker.PickSingleFolderAsync();
        if (folder is not null)
        {
            SetSource(folder.Path);
        }
    }

    private async void SelectOutputFolder_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FolderPicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
        };
        picker.FileTypeFilter.Add("*");
        InitializePicker(picker);

        var folder = await picker.PickSingleFolderAsync();
        if (folder is not null)
        {
            _outputDirectory = Path.Combine(folder.Path, $"ArbitraDocs_Analisis_{DateTime.Now:yyyyMMdd_HHmmss}");
            OutputFolderText.Text = _outputDirectory;
        }
    }

    private void DropZone_DragOver(object sender, DragEventArgs e)
    {
        if (e.DataView.Contains(StandardDataFormats.StorageItems))
        {
            e.AcceptedOperation = DataPackageOperation.Copy;
            e.DragUIOverride.Caption = "Analizar con ArbitraDocs";
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
        var item = items.FirstOrDefault();
        if (item is StorageFolder folder)
        {
            SetSource(folder.Path);
            return;
        }

        if (item is StorageFile file)
        {
            var extension = file.FileType.ToLowerInvariant();
            if (extension is ".zip" or ".rar" or ".pdf")
            {
                SetSource(file.Path);
                return;
            }
        }

        ShowStatus("Arrastra una carpeta o un archivo ZIP, RAR o PDF.", InfoBarSeverity.Warning);
    }

    private async void Analyze_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrWhiteSpace(_source))
        {
            ShowStatus("Primero selecciona el escrito y sus anexos.", InfoBarSeverity.Warning);
            return;
        }

        if (string.IsNullOrWhiteSpace(_outputDirectory))
        {
            ShowStatus("Selecciona una carpeta donde guardar los contratos, cláusulas, comprobantes y resumen.", InfoBarSeverity.Warning);
            return;
        }

        SetBusy(true);
        StatusBar.IsOpen = false;
        Contracts.Clear();
        Payments.Clear();
        ResetCounters();

        try
        {
            var result = await _engine.AnalyzeExpedientAsync(_source, _outputDirectory);
            foreach (var contract in result.Contracts)
            {
                Contracts.Add(contract);
            }
            foreach (var payment in result.Payments)
            {
                Payments.Add(payment);
            }

            DocumentsCountText.Text = result.DocumentsAnalyzed.ToString("N0");
            PagesCountText.Text = result.PagesAnalyzed.ToString("N0");
            OcrCountText.Text = result.OcrPages.ToString("N0");
            ContractsCountText.Text = result.Contracts.Count.ToString("N0");
            PaymentsCountText.Text = result.Payments.Count.ToString("N0");
            _outputDirectory = result.OutputDirectory;
            OutputFolderText.Text = result.OutputDirectory;
            OpenResultsButton.IsEnabled = Directory.Exists(result.OutputDirectory);

            if (result.Warnings.Count > 0)
            {
                ShowStatus(
                    $"Análisis terminado con {result.Warnings.Count} advertencia(s). {result.Warnings[0]}",
                    InfoBarSeverity.Warning);
            }
            else
            {
                ShowStatus(
                    $"Análisis terminado: {result.Contracts.Count} contrato(s) y {result.Payments.Count} comprobante(s) detectados.",
                    InfoBarSeverity.Success);
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

    private void OpenResults_Click(object sender, RoutedEventArgs e)
    {
        if (!string.IsNullOrWhiteSpace(_outputDirectory) && Directory.Exists(_outputDirectory))
        {
            Process.Start(new ProcessStartInfo("explorer.exe", _outputDirectory) { UseShellExecute = true });
        }
    }

    private void OpenGeneratedPdf_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button)
        {
            return;
        }

        var path = button.Tag?.ToString();
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
        {
            ShowStatus("No hay un PDF generado disponible para este elemento.", InfoBarSeverity.Informational);
            return;
        }

        Process.Start(new ProcessStartInfo(path) { UseShellExecute = true });
    }

    private void SetSource(string path)
    {
        _source = path;
        SourceText.Text = path;
        Contracts.Clear();
        Payments.Clear();
        ResetCounters();
        OpenResultsButton.IsEnabled = false;
        StatusBar.IsOpen = false;
    }

    private void SetBusy(bool busy)
    {
        BusyRing.IsActive = busy;
        BusyRing.Visibility = busy ? Visibility.Visible : Visibility.Collapsed;
        AnalyzeButton.IsEnabled = !busy;
        DropZone.IsHitTestVisible = !busy;
    }

    private void ResetCounters()
    {
        DocumentsCountText.Text = "0";
        PagesCountText.Text = "0";
        OcrCountText.Text = "0";
        ContractsCountText.Text = "0";
        PaymentsCountText.Text = "0";
    }

    private void ShowStatus(string message, InfoBarSeverity severity)
    {
        StatusBar.Message = message;
        StatusBar.Severity = severity;
        StatusBar.IsOpen = true;
    }

    private static void InitializePicker(object picker)
    {
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
        WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
    }
}
