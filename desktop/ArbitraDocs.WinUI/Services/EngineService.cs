using System.Diagnostics;
using System.Globalization;
using System.Text.Json;
using ArbitraDocs.WinUI.Models;

namespace ArbitraDocs.WinUI.Services;

public sealed record DocumentProcessOptions(
    bool NormalizeA4,
    bool PreserveExistingA4,
    double PageMarginMm,
    bool EnlargeSmallPages,
    bool Foliate,
    int StartNumber,
    string Direction,
    string Mode,
    string Position,
    string FontFamily,
    bool Bold,
    bool Italic,
    double FontSize,
    double FolioMarginXmm,
    double FolioMarginYmm,
    bool Certify,
    string CertificationMode,
    string? CertificatePdf,
    string? StampImage,
    string StampPosition,
    double StampWidthMm,
    double StampMarginXmm,
    double StampMarginYmm);

public sealed class EngineService
{
    public async Task<FileInventoryResult> MapFilesAsync(
        string source,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(source) || (!File.Exists(source) && !Directory.Exists(source)))
        {
            throw new ArgumentException("Selecciona una carpeta, ZIP o RAR válido.", nameof(source));
        }

        var enginePath = FindEngine();
        var tempJson = Path.Combine(Path.GetTempPath(), $"ArbitraDocs_inventory_{Guid.NewGuid():N}.json");
        try
        {
            await RunEngineAsync(
                enginePath,
                new[] { "map", source, tempJson },
                cancellationToken);

            var json = await File.ReadAllTextAsync(tempJson, cancellationToken);
            var result = JsonSerializer.Deserialize<FileInventoryResult>(
                json,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

            return result ?? throw new InvalidOperationException("El motor no devolvió un inventario válido.");
        }
        finally
        {
            try
            {
                if (File.Exists(tempJson))
                {
                    File.Delete(tempJson);
                }
            }
            catch
            {
                // Un temporal bloqueado no debe impedir mostrar el resultado.
            }
        }
    }

    public async Task<ExpedientAnalysisResult> AnalyzeExpedientAsync(
        string source,
        string outputDirectory,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(source) || (!File.Exists(source) && !Directory.Exists(source)))
        {
            throw new ArgumentException("Selecciona una carpeta, ZIP, RAR o PDF válido.", nameof(source));
        }

        if (string.IsNullOrWhiteSpace(outputDirectory))
        {
            throw new ArgumentException("Selecciona una carpeta donde guardar los resultados.", nameof(outputDirectory));
        }

        Directory.CreateDirectory(outputDirectory);
        var enginePath = FindEngine();
        var tempJson = Path.Combine(Path.GetTempPath(), $"ArbitraDocs_analysis_{Guid.NewGuid():N}.json");

        try
        {
            await RunEngineAsync(
                enginePath,
                new[] { "analyze-expedient", source, outputDirectory, tempJson },
                cancellationToken);

            var json = await File.ReadAllTextAsync(tempJson, cancellationToken);
            var result = JsonSerializer.Deserialize<ExpedientAnalysisResult>(
                json,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

            return result ?? throw new InvalidOperationException("El motor no devolvió un análisis válido.");
        }
        finally
        {
            try
            {
                if (File.Exists(tempJson))
                {
                    File.Delete(tempJson);
                }
            }
            catch
            {
                // El resultado ya quedó guardado en la carpeta elegida.
            }
        }
    }

    public async Task ProcessAsync(
        IReadOnlyList<string> inputSources,
        string outputPdf,
        DocumentProcessOptions options,
        CancellationToken cancellationToken = default)
    {
        if (inputSources.Count == 0)
        {
            throw new ArgumentException("No hay documentos para procesar.", nameof(inputSources));
        }

        if (options.Certify && options.CertificationMode == "reverse" &&
            (string.IsNullOrWhiteSpace(options.CertificatePdf) || !File.Exists(options.CertificatePdf)))
        {
            throw new ArgumentException("Selecciona un PDF de certificación válido.", nameof(options));
        }

        if (options.Certify && options.CertificationMode == "stamp" &&
            (string.IsNullOrWhiteSpace(options.StampImage) || !File.Exists(options.StampImage)))
        {
            throw new ArgumentException("Selecciona una imagen de sello válida.", nameof(options));
        }

        var enginePath = FindEngine();
        var tempRoot = Directory.CreateTempSubdirectory("ArbitraDocs_");

        try
        {
            var merged = Path.Combine(tempRoot.FullName, "01_merged.pdf");
            var mergeArgs = new List<string> { "merge", merged };
            mergeArgs.AddRange(inputSources);
            await RunEngineAsync(enginePath, mergeArgs, cancellationToken);

            var current = merged;

            if (options.NormalizeA4)
            {
                var normalized = Path.Combine(tempRoot.FullName, "02_a4.pdf");
                var args = new List<string>
                {
                    "normalize",
                    current,
                    normalized,
                    "--margin-mm",
                    Invariant(options.PageMarginMm),
                };

                if (!options.PreserveExistingA4)
                {
                    args.Add("--no-preserve-a4");
                }

                if (options.EnlargeSmallPages)
                {
                    args.Add("--enlarge-small");
                }

                await RunEngineAsync(enginePath, args, cancellationToken);
                current = normalized;
            }

            if (options.Foliate)
            {
                var folioOutput = options.Certify
                    ? Path.Combine(tempRoot.FullName, "03_folio.pdf")
                    : outputPdf;

                var args = new List<string>
                {
                    "foliate",
                    current,
                    folioOutput,
                    "--start",
                    options.StartNumber.ToString(CultureInfo.InvariantCulture),
                    "--direction",
                    options.Direction,
                    "--mode",
                    options.Mode,
                    "--position",
                    options.Position,
                    "--font-family",
                    options.FontFamily,
                    "--font-size",
                    Invariant(options.FontSize),
                    "--margin-x-mm",
                    Invariant(options.FolioMarginXmm),
                    "--margin-y-mm",
                    Invariant(options.FolioMarginYmm),
                };

                if (options.Bold)
                {
                    args.Add("--bold");
                }

                if (options.Italic)
                {
                    args.Add("--italic");
                }

                await RunEngineAsync(enginePath, args, cancellationToken);
                current = folioOutput;
            }

            if (options.Certify)
            {
                if (options.CertificationMode == "stamp")
                {
                    var args = new[]
                    {
                        "stamp-certify",
                        current,
                        options.StampImage!,
                        outputPdf,
                        "--position",
                        options.StampPosition,
                        "--width-mm",
                        Invariant(options.StampWidthMm),
                        "--margin-x-mm",
                        Invariant(options.StampMarginXmm),
                        "--margin-y-mm",
                        Invariant(options.StampMarginYmm),
                    };
                    await RunEngineAsync(enginePath, args, cancellationToken);
                }
                else
                {
                    await RunEngineAsync(
                        enginePath,
                        new[] { "certify", current, options.CertificatePdf!, outputPdf },
                        cancellationToken);
                }
            }
            else if (!options.Foliate)
            {
                File.Copy(current, outputPdf, overwrite: true);
            }
        }
        finally
        {
            try
            {
                tempRoot.Delete(recursive: true);
            }
            catch
            {
                // Un temporal bloqueado no debe invalidar un PDF ya generado.
            }
        }
    }

    private static string FindEngine()
    {
        var configured = Environment.GetEnvironmentVariable("ARBITRADOCS_ENGINE_PATH");
        if (!string.IsNullOrWhiteSpace(configured) && File.Exists(configured))
        {
            return configured;
        }

        var candidates = new[]
        {
            Path.Combine(AppContext.BaseDirectory, "Engine", "ArbitraDocs.Engine.exe"),
            Path.Combine(AppContext.BaseDirectory, "ArbitraDocs.Engine.exe"),
        };

        foreach (var candidate in candidates)
        {
            if (File.Exists(candidate))
            {
                return candidate;
            }
        }

        throw new FileNotFoundException(
            "No se encontró el motor documental de ArbitraDocs. Reinstala la aplicación o usa el paquete completo de la beta.");
    }

    private static async Task RunEngineAsync(
        string enginePath,
        IEnumerable<string> arguments,
        CancellationToken cancellationToken)
    {
        var startInfo = new ProcessStartInfo(enginePath)
        {
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
        };

        foreach (var argument in arguments)
        {
            startInfo.ArgumentList.Add(argument);
        }

        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException("No se pudo iniciar el motor documental.");

        var stdoutTask = process.StandardOutput.ReadToEndAsync(cancellationToken);
        var stderrTask = process.StandardError.ReadToEndAsync(cancellationToken);

        await process.WaitForExitAsync(cancellationToken);
        var stdout = await stdoutTask;
        var stderr = await stderrTask;

        if (process.ExitCode != 0)
        {
            var detail = string.IsNullOrWhiteSpace(stderr) ? stdout : stderr;
            throw new InvalidOperationException(
                string.IsNullOrWhiteSpace(detail)
                    ? $"El motor terminó con código {process.ExitCode}."
                    : detail.Trim());
        }
    }

    private static string Invariant(double value)
        => value.ToString("0.###", CultureInfo.InvariantCulture);
}
