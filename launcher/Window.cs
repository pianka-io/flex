using System.Text.Json;

namespace launcher;

public partial class Window : Form
{
    public Window()
    {
        InitializeComponent();
    }

    private Config LoadConfig()
    {
        var path = Path.Combine(Application.StartupPath, "flex.json");
        var json = File.ReadAllText(path);
        return JsonSerializer.Deserialize<Config>(json)!;
    }
    
    private void SaveConfig()
    {
        var path = Path.Combine(Application.StartupPath, "flex.json");
        var json = JsonSerializer.Serialize(new Config
        {
            DiabloII = txtDiabloII.Text,
            Flex = txtFlex.Text,
            Arguments = txtArguments.Text
        });
        File.WriteAllText(path, json);
    }
    
    private void Window_Load(object sender, EventArgs e)
    {
        var config = LoadConfig();
        txtDiabloII.Text = config.DiabloII;
        txtFlex.Text = config.Flex;
        txtArguments.Text = config.Arguments;
    }

    private void btnBrowseDiabloII_Click(object sender, EventArgs e)
    {
        using var dialog = new FolderBrowserDialog();
        dialog.InitialDirectory = txtDiabloII.Text;
        if (dialog.ShowDialog() == DialogResult.OK && !string.IsNullOrWhiteSpace(dialog.SelectedPath))
        {
            txtDiabloII.Text = dialog.SelectedPath;
        }
    }

    private void btnLaunch_Click(object sender, EventArgs e)
    {
        Injector.Launch(txtDiabloII.Text, txtFlex.Text, txtArguments.Text);
    }

    private void btnBrowseFlex_Click(object sender, EventArgs e)
    {
        using var dialog = new FolderBrowserDialog();
        dialog.InitialDirectory = txtFlex.Text;
        if (dialog.ShowDialog() == DialogResult.OK && !string.IsNullOrWhiteSpace(dialog.SelectedPath))
        {
            txtFlex.Text = dialog.SelectedPath;
        }
    }

    private void txtDiabloII_TextChanged(object sender, EventArgs e)
    {
        SaveConfig();
    }

    private void txtFlex_TextChanged(object sender, EventArgs e)
    {
        SaveConfig();
    }

    private void txtArguments_TextChanged(object sender, EventArgs e)
    {
        SaveConfig();
    }
}