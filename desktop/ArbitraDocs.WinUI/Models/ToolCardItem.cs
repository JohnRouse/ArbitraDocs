namespace ArbitraDocs.WinUI.Models;

public sealed class ToolCardItem
{
    public string Key { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public bool Available { get; set; }
    public string Status => Available ? "Disponible" : "Próximamente";
}
