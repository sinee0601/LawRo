package com.taba.lawro.components

import android.content.Context
import androidx.appcompat.app.AlertDialog
import androidx.core.content.ContextCompat
import com.taba.lawro.R

fun showAlertDialog(
    context: Context,
    title: String = "알림",
    message: String,
    positiveButtonText: String = "확인"
) {
    val dialog = AlertDialog.Builder(context)
        .setTitle(title)
        .setMessage(message)
        .setPositiveButton(positiveButtonText, null)
        .create()

    dialog.setOnShowListener {
        val positiveButton = dialog.getButton(AlertDialog.BUTTON_POSITIVE)
       positiveButton.setTextColor(
            ContextCompat.getColor(context, R.color.lawro_blue)
        )
    }

    dialog.show()
}