using System.Text.Json.Serialization;

namespace ArbitraDocs.WinUI.Models;

public sealed class ExpedientAnalysisResult
{
    [JsonPropertyName("source")]
    public string Source { get; set; } = string.Empty;

    [JsonPropertyName("output_directory")]
    public string OutputDirectory { get; set; } = string.Empty;

    [JsonPropertyName("documents_analyzed")]
    public int DocumentsAnalyzed { get; set; }

    [JsonPropertyName("pages_analyzed")]
    public int PagesAnalyzed { get; set; }

    [JsonPropertyName("ocr_pages")]
    public int OcrPages { get; set; }

    [JsonPropertyName("contracts")]
    public List<ContractDetection> Contracts { get; set; } = new();

    [JsonPropertyName("payments")]
    public List<PaymentDetection> Payments { get; set; } = new();

    [JsonPropertyName("warnings")]
    public List<string> Warnings { get; set; } = new();
}

public sealed class ContractDetection
{
    [JsonPropertyName("title")]
    public string Title { get; set; } = string.Empty;

    [JsonPropertyName("issue_date")]
    public string? IssueDate { get; set; }

    [JsonPropertyName("source_path")]
    public string SourcePath { get; set; } = string.Empty;

    [JsonPropertyName("start_page")]
    public int StartPage { get; set; }

    [JsonPropertyName("end_page")]
    public int EndPage { get; set; }

    [JsonPropertyName("arbitration_clause_pages")]
    public List<int> ArbitrationClausePages { get; set; } = new();

    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }

    [JsonPropertyName("output_pdf")]
    public string OutputPdf { get; set; } = string.Empty;

    [JsonPropertyName("clause_pdf")]
    public string? ClausePdf { get; set; }

    [JsonIgnore]
    public string PagesText => StartPage == EndPage ? StartPage.ToString() : $"{StartPage}-{EndPage}";

    [JsonIgnore]
    public string ClausePagesText => ArbitrationClausePages.Count == 0
        ? "No detectada"
        : string.Join(", ", ArbitrationClausePages);

    [JsonIgnore]
    public string ConfidenceText => $"{Confidence:P0}";

    [JsonIgnore]
    public string IssueDateText => string.IsNullOrWhiteSpace(IssueDate) ? "No detectada" : IssueDate;
}

public sealed class PaymentDetection
{
    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;

    [JsonPropertyName("date")]
    public string? Date { get; set; }

    [JsonPropertyName("amount")]
    public string? Amount { get; set; }

    [JsonPropertyName("operation")]
    public string? Operation { get; set; }

    [JsonPropertyName("source_path")]
    public string SourcePath { get; set; } = string.Empty;

    [JsonPropertyName("page")]
    public int Page { get; set; }

    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }

    [JsonPropertyName("output_pdf")]
    public string OutputPdf { get; set; } = string.Empty;

    [JsonIgnore]
    public string DateText => string.IsNullOrWhiteSpace(Date) ? "No detectada" : Date;

    [JsonIgnore]
    public string AmountText => string.IsNullOrWhiteSpace(Amount) ? "No detectado" : Amount;

    [JsonIgnore]
    public string OperationText => string.IsNullOrWhiteSpace(Operation) ? "No detectada" : Operation;

    [JsonIgnore]
    public string ConfidenceText => $"{Confidence:P0}";
}
