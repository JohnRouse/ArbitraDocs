using System.Text.Json.Serialization;

namespace ArbitraDocs.WinUI.Models;

public sealed class FileInventoryResult
{
    [JsonPropertyName("source")]
    public string Source { get; set; } = string.Empty;

    [JsonPropertyName("sourceType")]
    public string SourceType { get; set; } = string.Empty;

    [JsonPropertyName("root")]
    public FileInventoryNode Root { get; set; } = new();

    [JsonPropertyName("summary")]
    public FileInventorySummary Summary { get; set; } = new();

    [JsonPropertyName("warnings")]
    public List<string> Warnings { get; set; } = new();
}

public sealed class FileInventoryNode
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;

    [JsonPropertyName("path")]
    public string Path { get; set; } = string.Empty;

    [JsonPropertyName("extension")]
    public string Extension { get; set; } = string.Empty;

    [JsonPropertyName("size")]
    public long Size { get; set; }

    [JsonPropertyName("children")]
    public List<FileInventoryNode> Children { get; set; } = new();

    [JsonIgnore]
    public bool IsFolder => string.Equals(Type, "folder", StringComparison.OrdinalIgnoreCase);
}

public sealed class FileInventorySummary
{
    [JsonPropertyName("files")]
    public int Files { get; set; }

    [JsonPropertyName("folders")]
    public int Folders { get; set; }

    [JsonPropertyName("totalSize")]
    public long TotalSize { get; set; }

    [JsonPropertyName("extensions")]
    public Dictionary<string, int> Extensions { get; set; } = new();
}

public sealed class ExtensionSummaryItem
{
    public string Extension { get; set; } = string.Empty;
    public int Count { get; set; }
}

public sealed class InventorySearchItem
{
    public string Name { get; set; } = string.Empty;
    public string Path { get; set; } = string.Empty;
    public string Extension { get; set; } = string.Empty;
    public string SizeText { get; set; } = string.Empty;
}
