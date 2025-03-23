namespace launcher;

partial class Window
{
    /// <summary>
    ///  Required designer variable.
    /// </summary>
    private System.ComponentModel.IContainer components = null;

    /// <summary>
    ///  Clean up any resources being used.
    /// </summary>
    /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
    protected override void Dispose(bool disposing)
    {
        if (disposing && (components != null))
        {
            components.Dispose();
        }

        base.Dispose(disposing);
    }

    #region Windows Form Designer generated code

    /// <summary>
    /// Required method for Designer support - do not modify
    /// the contents of this method with the code editor.
    /// </summary>
    private void InitializeComponent()
    {
        txtDiabloII = new System.Windows.Forms.TextBox();
        lblDiabloII = new System.Windows.Forms.Label();
        btnBrowseDiabloII = new System.Windows.Forms.Button();
        btnBrowseFlex = new System.Windows.Forms.Button();
        lblFlex = new System.Windows.Forms.Label();
        txtFlex = new System.Windows.Forms.TextBox();
        lblDivider = new System.Windows.Forms.Label();
        btnLaunch = new System.Windows.Forms.Button();
        lblArguments = new System.Windows.Forms.Label();
        txtArguments = new System.Windows.Forms.TextBox();
        SuspendLayout();
        // 
        // txtDiabloII
        // 
        txtDiabloII.Location = new System.Drawing.Point(88, 16);
        txtDiabloII.Name = "txtDiabloII";
        txtDiabloII.Size = new System.Drawing.Size(231, 23);
        txtDiabloII.TabIndex = 0;
        txtDiabloII.TextChanged += txtDiabloII_TextChanged;
        // 
        // lblDiabloII
        // 
        lblDiabloII.Location = new System.Drawing.Point(14, 16);
        lblDiabloII.Name = "lblDiabloII";
        lblDiabloII.Size = new System.Drawing.Size(68, 23);
        lblDiabloII.TabIndex = 1;
        lblDiabloII.Text = "Diablo II";
        lblDiabloII.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
        // 
        // btnBrowseDiabloII
        // 
        btnBrowseDiabloII.Location = new System.Drawing.Point(325, 16);
        btnBrowseDiabloII.Name = "btnBrowseDiabloII";
        btnBrowseDiabloII.Size = new System.Drawing.Size(83, 23);
        btnBrowseDiabloII.TabIndex = 2;
        btnBrowseDiabloII.Text = "Browse...";
        btnBrowseDiabloII.UseVisualStyleBackColor = true;
        btnBrowseDiabloII.Click += btnBrowseDiabloII_Click;
        // 
        // btnBrowseFlex
        // 
        btnBrowseFlex.Location = new System.Drawing.Point(325, 45);
        btnBrowseFlex.Name = "btnBrowseFlex";
        btnBrowseFlex.Size = new System.Drawing.Size(83, 23);
        btnBrowseFlex.TabIndex = 5;
        btnBrowseFlex.Text = "Browse...";
        btnBrowseFlex.UseVisualStyleBackColor = true;
        btnBrowseFlex.Click += btnBrowseFlex_Click;
        // 
        // lblFlex
        // 
        lblFlex.Location = new System.Drawing.Point(14, 45);
        lblFlex.Name = "lblFlex";
        lblFlex.Size = new System.Drawing.Size(68, 23);
        lblFlex.TabIndex = 4;
        lblFlex.Text = "Flex";
        lblFlex.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
        // 
        // txtFlex
        // 
        txtFlex.Location = new System.Drawing.Point(88, 45);
        txtFlex.Name = "txtFlex";
        txtFlex.Size = new System.Drawing.Size(231, 23);
        txtFlex.TabIndex = 3;
        txtFlex.TextChanged += txtFlex_TextChanged;
        // 
        // lblDivider
        // 
        lblDivider.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
        lblDivider.Location = new System.Drawing.Point(-8, 110);
        lblDivider.Name = "lblDivider";
        lblDivider.Size = new System.Drawing.Size(445, 2);
        lblDivider.TabIndex = 6;
        // 
        // btnLaunch
        // 
        btnLaunch.Location = new System.Drawing.Point(325, 120);
        btnLaunch.Name = "btnLaunch";
        btnLaunch.Size = new System.Drawing.Size(83, 23);
        btnLaunch.TabIndex = 7;
        btnLaunch.Text = "Launch";
        btnLaunch.UseVisualStyleBackColor = true;
        btnLaunch.Click += btnLaunch_Click;
        // 
        // lblArguments
        // 
        lblArguments.Location = new System.Drawing.Point(14, 74);
        lblArguments.Name = "lblArguments";
        lblArguments.Size = new System.Drawing.Size(68, 23);
        lblArguments.TabIndex = 9;
        lblArguments.Text = "Arguments";
        lblArguments.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
        // 
        // txtArguments
        // 
        txtArguments.Location = new System.Drawing.Point(88, 74);
        txtArguments.Name = "txtArguments";
        txtArguments.Size = new System.Drawing.Size(320, 23);
        txtArguments.TabIndex = 8;
        txtArguments.TextChanged += txtArguments_TextChanged;
        // 
        // Window
        // 
        AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
        AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
        ClientSize = new System.Drawing.Size(424, 152);
        Controls.Add(lblArguments);
        Controls.Add(txtArguments);
        Controls.Add(btnLaunch);
        Controls.Add(lblDivider);
        Controls.Add(btnBrowseFlex);
        Controls.Add(lblFlex);
        Controls.Add(txtFlex);
        Controls.Add(btnBrowseDiabloII);
        Controls.Add(lblDiabloII);
        Controls.Add(txtDiabloII);
        MaximizeBox = false;
        StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
        Text = "Flex 0.1a";
        Load += Window_Load;
        ResumeLayout(false);
        PerformLayout();
    }

    private System.Windows.Forms.Label lblArguments;
    private System.Windows.Forms.TextBox txtArguments;

    private System.Windows.Forms.Button btnLaunch;

    private System.Windows.Forms.Label lblDivider;

    private System.Windows.Forms.Button btnBrowseDiabloII;
    private System.Windows.Forms.Button btnBrowseFlex;
    private System.Windows.Forms.Label lblFlex;
    private System.Windows.Forms.TextBox txtFlex;

    private System.Windows.Forms.Label lblDiabloII;

    private System.Windows.Forms.TextBox txtDiabloII;

    #endregion
}