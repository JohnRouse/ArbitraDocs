namespace ArbitraDocs.WinUI.Models;

public sealed class ToolCardItem
{
    public required string Key { get; init; }
    public required string Name { get; init; }
    public required string Description { get; init; }
    public bool Available { get; init; }
    public string Status => Available ? "Disponible" : "Próximamente";
}
