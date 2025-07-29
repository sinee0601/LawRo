package com.taba.lawro.selectLanguage

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.HorizontalDivider
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.taba.lawro.R
import java.util.*

data class Language(
    val code: String,
    val displayName: String,
    val nativeName: String
)

@Composable
fun SelectLanguageScreen(
    onLanguageSelected: (String) -> Unit = {}
) {
    var selectedLanguage by remember { mutableStateOf<Language?>(null) }
    val scrollState = rememberScrollState()
    
    val languages = listOf(
        Language("en", "ENGLISH", "영어"),
        Language("ja", "日本語", "일본어"),
        Language("zh", "中文", "중국어"),
        Language("vi", "Tiếng Việt", "베트남어"),
        Language("th", "ภاษาไทย", "태국어"),
        Language("ko", "KOREAN", "한국어")
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .verticalScroll(scrollState)
            .padding(horizontal = 24.dp)  
    ) {
        Spacer(modifier = Modifier.height(100.dp))

        // Title with Logo
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 16.dp,bottom = 16.dp ,end = 60.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Image(
                painter = painterResource(id = R.drawable.select_language_logo),
                contentDescription = "Select language logo",
                modifier = Modifier.size(60.dp)
            )
            Spacer(modifier = Modifier.width(1.dp))
            Text(
                text = "언어 선택",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Language list
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            languages.forEachIndexed { index, language ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { selectedLanguage = language },
                    colors = CardDefaults.cardColors(
                        containerColor = if (selectedLanguage == language) 
                            Color(0xFFE8F1FF) else Color.White
                    ),
                    shape = RoundedCornerShape(8.dp),
                    elevation = CardDefaults.cardElevation(
                        defaultElevation = 2.dp
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 12.dp, horizontal = 16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // 각 언어별 국기 아이콘 표시
                        val flagResource = when (language.code) {
                            "en" -> R.drawable.ic_us
                            "ja" -> R.drawable.ic_jp
                            "zh" -> R.drawable.ic_ch
                            "vi" -> R.drawable.ic_vi
                            "th" -> R.drawable.ic_th
                            "ko" -> R.drawable.ic_ko
                            else -> null
                        }
                        
                        flagResource?.let {
                            Image(
                                painter = painterResource(id = it),
                                contentDescription = "${language.displayName} Flag",
                                modifier = Modifier.size(32.dp)
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                        }
                        
                        Column {
                            Text(
                                text = language.displayName,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Normal
                            )
                            Text(
                                text = language.nativeName,
                                fontSize = 14.sp,
                                color = Color.Gray
                            )
                        }
                    }
                }
                
                if (index == languages.lastIndex) {
                    Spacer(modifier = Modifier.height(16.dp))
                    HorizontalDivider(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 8.dp),
                        color = Color(0xFFCCCCCC),
                        thickness = 2.dp
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(60.dp))
        Button(
            onClick = { 
                selectedLanguage?.let { onLanguageSelected(it.code) }
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 52.dp)
                .height(48.dp),
            enabled = selectedLanguage != null,
            shape = RoundedCornerShape(12.dp)
        ) {
            Text(
                text = "선택",
                fontSize = 16.sp
            )
        }
    }
}
