using System.Collections.ObjectModel;
using System.Text;
using System.Text.Json;
using ArbitraDocs.WinUI.Models;
using ArbitraDocs.WinUI.Services;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;
using Windows.Storage.Pickers;

namespace ArbitraDocs.WinUI.Pages;

public sealed partial class FileInventoryPage : Page
{
    public ObservableCollection<ExtensionSummaryItem> ExtensionSummary { get; } = new();
    public ObservableCollection<InventorySearchItem> SearchResults { get; } = new();

    private readonly EngineService _engine = new();
    private readonly List<FileInventoryNode> _flatNodes = new();
    private FileInventoryResult? _inventory;

    public FileInventoryPage()
    {
        InitializeComponent();
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
            await AnalyzeAsync(folder.Path);
        }
    }

    private async void SelectArchive_Click(object sender, RoutedEventArgs e)
    {
        var picker = new FileOpenPicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
            ViewMode = PickerViewMode.List,
        };
        picker.FileTypeFilter.Add(".zip");
        picker.FileTypeFilter.Add(".rar");
        InitializePicker(picker);

        var file = await picker.PickSingleFileAsync();
        if (file is not null)
        {
            await AnalyzeAsync(file.Path);
        }
    }

    private void DropZone_DragOver(object sender, DragEventArgs e)
    {
        if (e.DataView.Contains(StandardDataFormats.StorageItems))
        {
            e.AcceptedOperation = DataPackageOperation.Copy;
            e.DragUIOverride.Caption = "Mapear con ArbitraDocs";
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
        foreach (var item in items)
        {
            if (item is StorageFolder folder)
            {
                await AnalyzeAsync(folder.Path);
                return;
            }

            if (item is StorageFile file &&
                (string.Equals(file.FileType, ".zip", StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(file.FileType, ".rar", StringComparison.OrdinalIgnoreCase)))
            {
                await AnalyzeAsync(file.Path);
                return;
            }
        }

        ShowStatus("Arrastra una carpeta o un archivo ZIP/RAR.", InfoBarSeverity.Warning);
    }

    private async Task AnalyzeAsync(string source)
    {
        SetBusy(true);
        StatusBar.IsOpen = false;
        SourceText.Text = source;

        try
        {
            var result = await _engine.MapFilesAsync(source);
            RenderInventory(result);

            if (result.Warnings.Count > 0)
            {
                ShowStatus(
                    $"Inventario generado con {result.Warnings.Count} advertencia(s). {result.Warnings[0]}",
                    InfoBarSeverity.Warning);
            }
            else
            {
                ShowStatus("Inventario generado correctamente. No se modificó ningún archivo original.", InfoBarSeverity.Success);
            }
        }
        catch (Exception ex)
        {
            ClearInventory();
            ShowStatus(ex.Message, InfoBarSeverity.Error);
        }
        finally
        {
            SetBusy(false);
        }
    }

    private void RenderInventory(FileInventoryResult inventory)
    {
        _inventory = inventory;
        _flatNodes.Clear();
        Flatten(inventory.Root, _flatNodes);

        FilesCountText.Text = inventory.Summary.Files.ToString("N0");
        FoldersCountText.Text = inventory.Summary.Folders.ToString("N0");
        TotalSizeText.Text = FormatBytes(inventory.Summary.TotalSize);
        ExtensionsCountText.Text = inventory.Summary.Extensions.Count.ToString("N0");

        InventoryTree.RootNodes.Clear();
        var root = BuildTreeNode(inventory.Root, 0);
        root.IsExpanded = true;
        InventoryTree.RootNodes.Add(root);

        ExtensionSummary.Clear();
        foreach (var item in inventory.Summary.Extensions
                     .OrderByDescending(pair => pair.Value)
                     .ThenBy(pair => pair.Key, StringComparer.CurrentCultureIgnoreCase))
        {
            ExtensionSummary.Add(new ExtensionSummaryItem
            {
                Extension = item.Key,
                Count = item.Value,
            });
        }

        SearchBox.Text = string.Empty;
        SearchResults.Clear();
        SetExportEnabled(true);
    }

    private TreeViewNode BuildTreeNode(FileInventoryNode item, int depth)
    {
        var label = item.IsFolder
            ? item.Name
            : $"{item.Name}   ·   {FormatBytes(item.Size)}";

        var node = new TreeViewNode
        {
            Content = label,
            IsExpanded = depth < 1,
        };

        foreach (var child in item.Children)
        {
            node.Children.Add(BuildTreeNode(child, depth + 1));
        }

        return node;
    }

    private void SearchBox_TextChanged(object sender, TextChangedEventArgs e)
    {
        SearchResults.Clear();
        if (_inventory is null)
        {
            return;
        }

        var query = SearchBox.Text.Trim();
        if (query.Length == 0)
        {
            return;
        }

        foreach (var node in _flatNodes
                     .Where(node => !node.IsFolder)
                     .Where(node =>
                         node.Name.Contains(query, StringComparison.CurrentCultureIgnoreCase) ||
                         node.Path.Contains(query, StringComparison.CurrentCultureIgnoreCase) ||
                         node.Extension.Contains(query, StringComparison.CurrentCultureIgnoreCase))
                     .Take(500))
        {
            SearchResults.Add(new InventorySearchItem
            {
                Name = node.Name,
                Path = node.Path,
                Extension = node.Extension,
                SizeText = FormatBytes(node.Size),
            });
        }
    }

    private async void ExportTxt_Click(object sender, RoutedEventArgs e)
        => await ExportAsync("txt");

    private async void ExportCsv_Click(object sender, RoutedEventArgs e)
        => await ExportAsync("csv");

    private async void ExportJson_Click(object sender, RoutedEventArgs e)
        => await ExportAsync("json");

    private async Task ExportAsync(string format)
    {
        if (_inventory is null)
        {
            return;
        }

        var picker = new FileSavePicker
        {
            SuggestedStartLocation = PickerLocationId.DocumentsLibrary,
            SuggestedFileName = $"Inventario_{System.IO.Path.GetFileNameWithoutExtension(_inventory.Root.Name)}",
        };

        switch (format)
        {
            case "csv":
                picker.FileTypeChoices.Add("Archivo CSV", new List<string> { ".csv" });
                break;
            case "json":
                picker.FileTypeChoices.Add("Archivo JSON", new List<string> { ".json" });
                break;
            default:
                picker.FileTypeChoices.Add("Archivo de texto", new List<string> { ".txt" });
                break;
        }

        InitializePicker(picker);
        var file = await picker.PickSaveFileAsync();
        if (file is null)
        {
            return;
        }

        string content = format switch
        {
            "csv" => BuildCsv(_inventory),
            "json" => JsonSerializer.Serialize(_inventory, new JsonSerializerOptions { WriteIndented = true }),
            _ => BuildTreeText(_inventory),
        };

        await File.WriteAllTextAsync(file.Path, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: true));
        ShowStatus($"Inventario exportado: {file.Name}", InfoBarSeverity.Success);
    }

    private static string BuildCsv(FileInventoryResult inventory)
    {
        var nodes = new List<FileInventoryNode>();
        Flatten(inventory.Root, nodes);
        var sb = new StringBuilder();
        sb.AppendLine("Tipo,Nombre,Extensión,Tamaño (bytes),Ruta");
        foreach (var node in nodes.Skip(1))
        {
            sb.Append(Csv(node.IsFolder ? "Carpeta" : "Archivo")).Append(',')
              .Append(Csv(node.Name)).Append(',')
              .Append(Csv(node.Extension)).Append(',')
              .Append(node.Size).Append(',')
              .Append(Csv(node.Path)).AppendLine();
        }
        return sb.ToString();
    }

    private static string BuildTreeText(FileInventoryResult inventory)
    {
        var sb = new StringBuilder();
        sb.AppendLine(inventory.Root.Name);
        AppendChildren(sb, inventory.Root.Children, string.Empty);
        sb.AppendLine();
        sb.AppendLine($"Archivos: {inventory.Summary.Files:N0}");
        sb.AppendLine($"Carpetas: {inventory.Summary.Folders:N0}");
        sb.AppendLine($"Tamaño total: {FormatBytes(inventory.Summary.TotalSize)}");
        return sb.ToString();
    }

    private static void AppendChildren(StringBuilder sb, IReadOnlyList<FileInventoryNode> children, string prefix)
    {
        for (var index = 0; index < children.Count; index++)
        {
            var child = children[index];
            var last = index == children.Count - 1;
            sb.Append(prefix).Append(last ? "└── " : "├── ").Append(child.Name);
            if (!child.IsFolder)
            {
                sb.Append(" [").Append(child.Extension).Append(", ").Append(FormatBytes(child.Size)).Append(']');
            }
            sb.AppendLine();
            if (child.Children.Count > 0)
            {
                AppendChildren(sb, child.Children, prefix + (last ? "    " : "│   "));
            }
        }
    }

    private static string Csv(string value)
        => $"\"{value.Replace("\"", "\"\"")}\"";

    private static void Flatten(FileInventoryNode node, ICollection<FileInventoryNode> target)
    {
        target.Add(node);
        foreach (var child in node.Children)
        {
            Flatten(child, target);
        }
    }

    private static string FormatBytes(long bytes)
    {
        if (bytes < 1024)
        {
            return $"{bytes:N0} B";
        }

        double value = bytes;
        string[] units = { "KB", "MB", "GB", "TB" };
        foreach (var unit in units)
        {
            value /= 1024d;
            if (value < 1024d || unit == units[^1])
            {
                return $"{value:0.##} {unit}";
            }
        }
        return $"{bytes:N0} B";
    }

    private void ClearInventory()
    {
        _inventory = null;
        _flatNodes.Clear();
        InventoryTree.RootNodes.Clear();
        ExtensionSummary.Clear();
        SearchResults.Clear();
        FilesCountText.Text = "0";
        FoldersCountText.Text = "0";
        TotalSizeText.Text = "0 B";
        ExtensionsCountText.Text = "0";
        SetExportEnabled(false);
    }

    private void SetExportEnabled(bool enabled)
    {
        ExportTxtButton.IsEnabled = enabled;
        ExportCsvButton.IsEnabled = enabled;
        ExportJsonButton.IsEnabled = enabled;
    }

    private void SetBusy(bool busy)
    {
        BusyRing.IsActive = busy;
        BusyRing.Visibility = busy ? Visibility.Visible : Visibility.Collapsed;
        DropZone.IsHitTestVisible = !busy;
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
