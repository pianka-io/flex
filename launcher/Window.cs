namespace launcher;

public partial class Window : Form
{
    public Window()
    {
        InitializeComponent();
    }

    private void Window_Load(object sender, EventArgs e)
    {
        txtDiabloII.Text = @"C:\Users\Rick Pianka\Diablo II\Diablo II (1.13c)";
        // txtDiabloII.Text = @"C:\Program Files (x86)\Diablo II";
        txtFlex.Text = Path.GetDirectoryName(Application.ExecutablePath);
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
}